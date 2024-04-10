import hashlib
import os
import time
import json
from typing import List  # noqa: F401

from constants import LOOTBOX_TOKEN_PREFIX, PREMIUM_ENTITLEMENTS
from nations import NAMES as NATIONS_NAMES

from gui.goodies.goodie_items import PersonalVehicleDiscount
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN
from gui.shared.money import Currency, Money
from gui.shared.utils.requesters.blueprints_requester import getUniqueBlueprints
from gui.shared.formatters.time_formatters import RentDurationKeys
from messenger.formatters.service_channel_helpers import getCustomizationItem

from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.goodies import IGoodiesCache

from items import vehicles as vehicles_core, ITEM_TYPES, tankmen

from ..wotHookEvents import wotHookEvents
from ...utils import print_warn
from ...common.exceptionSending import with_exception_sending
from ..events import OnLootboxOpen
from ..eventLogger import eventLogger
from ..utils import setup_hangar_event, setup_session_meta


ALL_CURRENCIES = [ Currency.CREDITS, Currency.GOLD, Currency.FREE_XP, Currency.CRYSTAL, Currency.EVENT_COIN, Currency.BPCOIN, Currency.EQUIP_COIN ]


def getVehicleInfos(vehicles):
  addVehNames = []
  removeVehNames = []
  rentedVehNames = []
  compensatedVehicles = []

  def getRentInfo(rentData):
    # type: (dict) -> (str, int)

    timeLeft = rentData.get(RentDurationKeys.TIME, 0)
    if timeLeft:
      return ('time', int(timeLeft))
    else:
      for rentType in [RentDurationKeys.WINS, RentDurationKeys.BATTLES, RentDurationKeys.DAYS]:
        rentTypeValue = rentData.get(rentType, 0)
        if rentTypeValue > 0 and rentType != float('inf'):
          return (rentType, rentTypeValue)

  for vehicleDict in vehicles:
    for vehCompDescr, vehData in vehicleDict.iteritems():
      tankTag = vehicles_core.getVehicleType(abs(vehCompDescr)).name

      if b'rentCompensation' in vehData:
        comp = Money.makeFromMoneyTuple(vehData[b'rentCompensation'])
        compensatedVehicles.append((tankTag, 'rent', comp.gold))
        continue

      if b'customCompensation' in vehData:
        comp = Money.makeFromMoneyTuple(vehData[b'customCompensation'])
        compensatedVehicles.append((tankTag, 'normal', comp.gold))
        continue


      isNegative = vehCompDescr < 0
      isRented = 'rent' in vehData

      if isNegative:
        removeVehNames.append(tankTag)
      elif isRented:
        rentData = vehData['rent']
        rentType, rentValue = getRentInfo(rentData)
        rentedVehNames.append((tankTag, rentType, rentValue))
      else:
        addVehNames.append(tankTag)

  return (addVehNames, removeVehNames, rentedVehNames, compensatedVehicles)

def getGoodiesString(goodies, itemsCache, goodiesCache):
  # type: (dict, IItemsCache, IGoodiesCache) -> str
  boosters = []
  discounts = []
  equip = []
  
  for goodieID, ginfo in goodies.iteritems():
    if goodieID in itemsCache.items.shop.boosters:
      booster = goodiesCache.getBooster(goodieID)
      if booster is not None and booster.enabled:
        count = ginfo.get('count', 0)
        boosters.append((booster.boosterGuiType, booster.effectTime, booster.effectValue, count))

    elif goodieID in itemsCache.items.shop.discounts:
      discount = goodiesCache.getDiscount(goodieID)
      if discount is not None and discount.enabled:
        if isinstance(discount, PersonalVehicleDiscount):
          target = discount.targetValue
          tag = vehicles_core.getVehicleType(target).name
          discounts.append((tag, discount.effectValue))
          
    elif goodieID in itemsCache.items.shop.demountKits:
      dk = goodiesCache.getDemountKit(goodieID)
      if dk and dk.enabled:
        equip.append((dk.itemTypeName, ginfo.get('count', 0)))
        
    elif goodieID in itemsCache.items.shop.recertificationForms:
      rf = goodiesCache.getRecertificationForm(goodieID)
      if rf and rf.enabled:
        equip.append((dk.itemTypeName, ginfo.get('count', 0)))

  return (boosters, discounts, equip)

class OnLootboxLogger:

  itemsCache = dependency.descriptor(IItemsCache)
  goodiesCache = dependency.descriptor(IGoodiesCache)

  lastOpenId = None
  lastOpenCount = None

  def __init__(self):
    wotHookEvents.LootBoxOpenProcessorOpenRequest += self.on_request
    wotHookEvents.LootBoxOpenProcessorOpenResponse += self.on_response
  
  def on_request(self, obj, *a, **k):
    self.lastOpenId = obj._LootBoxOpenProcessor__lootBox.getID()
    self.lastOpenCount = obj._LootBoxOpenProcessor__count

  def on_response(self, obj, code, ctx=None):
    if ctx is None:
      print_warn('OnLootboxLogger.on_response: ctx is None')
      return
    
    if self.lastOpenId is None or self.lastOpenCount is None:
      print_warn('OnLootboxLogger.on_response: lastOpenId or lastOpenCount is None')
      return
     
    bonuses = ctx.get('bonus', []) # type: List[dict]

    lootboxType = self.itemsCache.items.tokens.getLootBoxByID(self.lastOpenId).getType()

    unique_bytes = str(time.time()).encode('utf-8') + os.urandom(16)
    groupId = hashlib.md5(unique_bytes).hexdigest()

    for bonus in bonuses:
      parsed = {}

      self.parseCurrency(parsed, bonus)
      self.parsePremium(parsed, bonus)
      self.parseVehicles(parsed, bonus)
      self.parseSlots(parsed, bonus)
      self.parseBerths(parsed, bonus)
      self.parseItems(parsed, bonus)
      self.parseGoodies(parsed, bonus)
      self.parseTokens(parsed, bonus)
      self.parseEntitlements(parsed, bonus)
      self.parseCustomizations(parsed, bonus)
      self.parseTankmen(parsed, bonus)
      self.parseEnhancements(parsed, bonus)
      self.parseBlueprints(parsed, bonus)
      self.parseSelectableCrewbook(parsed, bonus)
      self.parseDogtags(parsed, bonus)

      event = OnLootboxOpen(lootboxType, self.lastOpenCount, groupId)
      event.setup(json.dumps(bonus, ensure_ascii=False), parsed)
      setup_session_meta(event)
      setup_hangar_event(event)

      eventLogger.emit_event(event)


  @with_exception_sending
  def parseCurrency(self, parsed, bonus):
    for currenciesKey in ALL_CURRENCIES:
      parsed[currenciesKey] = bonus.get(currenciesKey, 0)

    platformCurrencies = bonus.get('currencies', {})
    parsed['currencies'] = [[currency, int(countDict)] for currency, countDict in platformCurrencies.iteritems()]
  
  @with_exception_sending
  def parsePremium(self, parsed, bonus):
    for premiumType in PREMIUM_ENTITLEMENTS.ALL_TYPES:
      parsed[premiumType] = bonus.get(premiumType, 0)

  @with_exception_sending
  def parseVehicles(self, parsed, bonus):
    vehiclesList = bonus.get('vehicles', [])
    addVehNames, removeVehNames, rentedVehNames, compensatedVehicles = getVehicleInfos(vehiclesList)
    parsed['addedVehicles'] = addVehNames
    parsed['rentedVehicles'] = rentedVehNames
    parsed['compensatedVehicles'] = compensatedVehicles

  @with_exception_sending
  def parseSlots(self, parsed, bonus):
    parsed['slots'] = bonus.get('slots', 0)

  @with_exception_sending
  def parseBerths(self, parsed, bonus):
    parsed['berths'] = bonus.get('berths', 0)

  @with_exception_sending
  def parseItems(self, parsed, bonus):
    parsed['items'] = []
    parsed['crewBooks'] = []
    items = bonus.get('items', {})

    for intCD, count in items.iteritems():
      itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
      if itemTypeID == ITEM_TYPES.crewBook:
        crewBook = tankmen.getItemByCompactDescr(intCD)
        parsed['crewBooks'].append((crewBook.getUserName(), count))
      else:
        parsed['items'].append((vehicles_core.getItemByCompactDescr(intCD).name, count))

  @with_exception_sending
  def parseGoodies(self, parsed, bonus):
      goodies = bonus.get('goodies', {})
      boosters, discounts, equip = getGoodiesString(goodies, self.itemsCache, self.goodiesCache)
      parsed['boosters'] = boosters
      parsed['discounts'] = discounts
      parsed['equip'] = equip

  @with_exception_sending
  def parseTokens(self, parsed, bonus):
    parsed['lootboxesTokens'] = []
    parsed['bonusTokens'] = []
    tokens = bonus.get('tokens', {})

    for tokenID, tokenData in tokens.iteritems():
      count = tokenData.get('count', 0)

      if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
        if str(self.lastOpenId) == tokenID.split(':')[1]:
          count += 1

        if count != 0:
          parsed['lootboxesTokens'].append((self.itemsCache.items.tokens.getLootBoxByTokenID(tokenID).getType(), count))
        
      elif tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
        parsed['bonusTokens'].append(('battle_bonus_x5', count))
      elif tokenID.startswith(CREW_BONUS_X3_TOKEN):
        parsed['bonusTokens'].append(('crew_bonus_x3', count))

  # TODO: Entitlements
  @with_exception_sending
  def parseEntitlements(self, parsed, bonus):
    # entitlementsList = [ (eID, eData.get('count', 0)) for eID, eData in bonus.get('entitlements', {}).iteritems() ]
    pass

  @with_exception_sending
  def parseCustomizations(self, parsed, bonus):
    parsed['customizations'] = []
    customizations = bonus.get('customizations', [])
    for customizationItem in customizations:
      splittedCustType = customizationItem.get('custType', '').split(':')
      custType = splittedCustType[0]
      count = customizationItem['value']
      if len(splittedCustType) == 2 and 'progression' in splittedCustType[1]:
          continue

      item = getCustomizationItem(customizationItem['id'], custType)

      parsed['customizations'].append((item.itemFullTypeName, item.descriptor.userKey, count))

  # TODO: Tankmen 
  @with_exception_sending
  def parseTankmen(self, parsed, bonus):
    # tankmen = bonus.get('tankmen', {})
    pass

  # TODO: Enhancements
  @with_exception_sending
  def parseEnhancements(self, parsed, bonus):
    # enhancements = bonus.get('enhancements', {})
    pass
    
  @with_exception_sending
  def parseBlueprints(self, parsed, bonus):
    parsed['blueprints'] = []
    blueprints = bonus.get('blueprints', {})
    vehicleFragments, nationFragments, universalFragments = getUniqueBlueprints(blueprints)
    for fragmentCD, count in vehicleFragments.iteritems():
      parsed['blueprints'].append(('VEHICLE', vehicles_core.getVehicleType(fragmentCD).name, count))

    for nationID, count in nationFragments.iteritems():
      parsed['blueprints'].append(('NATION', NATIONS_NAMES[nationID], count))

    if universalFragments:
      parsed['blueprints'].append(('UNIVERSAL', 'ANY', universalFragments))

  @with_exception_sending
  def parseSelectableCrewbook(self, parsed, bonus):
    selectableCrewbook = bonus.get('selectableCrewbook', {})
    parsed['selectableCrewbook'] = [crewbookName for crewbookName, data in selectableCrewbook.iteritems()]
  
  # TODO: dogtags
  @with_exception_sending
  def parseDogtags(self, parsed, bonus):
    # dogtags = bonus.get('dogTagComponents', {})
    pass


onLootboxLogger = OnLootboxLogger()
