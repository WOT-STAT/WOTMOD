import BattleReplay
import BigWorld
from PlayerEvents import g_playerEvents
from items import vehicles as vehiclesWG
from ..eventLogger import eventLogger
from ..events import OnBattleResult
from ..sessionStorage import sessionStorage
from ..utils import short_tank_type, setup_dynamic_battle_info, setup_session_meta
from ...common.exceptionSending import with_exception_sending
from ...utils import print_log, print_debug


class OnBattleResultLogger:
  arenas_id_wait_battle_result = []
  battle_loaded = False

  def __init__(self):
    self.arenas_id_wait_battle_result = []
    self.precreated_battle_result_event = dict()
    self.battle_loaded = False

    g_playerEvents.onBattleResultsReceived += self.on_battle_results_received
    eventLogger.on_session_created += self.on_session_created
    self.battle_result_cache_checker()

  def on_session_created(self, battleEventSession):
    self.arenas_id_wait_battle_result.append(battleEventSession.arenaID)
    event = OnBattleResult()
    setup_dynamic_battle_info(event)
    self.precreated_battle_result_event[battleEventSession.arenaID] = event

  @with_exception_sending
  def on_battle_results_received(self, isPlayerVehicle, results):
    if not isPlayerVehicle or BattleReplay.isPlaying():
      return
    self.process_battle_result(results)

  @with_exception_sending
  def battle_result_cache_checker(self):
    BigWorld.callback(3, self.battle_result_cache_checker)

    def result_callback(arenaID, code, result):
      if code > 0:
        self.process_battle_result(result)

    if len(self.arenas_id_wait_battle_result) > 0:
      arenaID = self.arenas_id_wait_battle_result.pop(0)
      self.arenas_id_wait_battle_result.append(arenaID)
      try:
        BigWorld.player().battleResultsCache.get(arenaID, lambda code, battleResults: result_callback(arenaID, code,
                                                                                                      battleResults))
      except:
        pass


  def process_battle_result(self, results):
    arenaID = results.get('arenaUniqueID')
    print_debug("Got result for {}".format(arenaID))

    if arenaID not in self.arenas_id_wait_battle_result:
      return

    self.arenas_id_wait_battle_result.remove(arenaID)
    battleEvent = self.precreated_battle_result_event.pop(arenaID)  # type: OnBattleResult

    decodeResult = {}
    try:
      winnerTeam = results['common']['winnerTeam']
      playerTeam = results['personal']['avatar']['team']
      winnerTeamIsMy = playerTeam == winnerTeam
      teamHealth = [results['common']['teamHealth'][1], results['common']['teamHealth'][2]]

      players = results['players']
      vehicles = results['vehicles']
      playersResultList = list()

      squadStorage = dict()
      squadCount = 0
      for playerID in players:
        squadID = players[playerID]['prebattleID']
        if squadID != 0 and squadID not in squadStorage:
          squadCount += 1
          squadStorage[squadID] = squadCount


      def getVehicleInfo(vehicle):
        veWG = vehiclesWG.getVehicleType(vehicle['typeCompDescr'])
        return {
          'spotted': vehicle['spotted'],
          'lifeTime': vehicle['lifeTime'],
          'mileage': vehicle['mileage'],
          'damageBlockedByArmor': vehicle['damageBlockedByArmor'],
          'damageAssistedRadio': vehicle['damageAssistedRadio'],
          'damageAssistedTrack': vehicle['damageAssistedTrack'],
          'damageAssistedStun': vehicle['damageAssistedStun'],
          'damageReceivedFromInvisibles': vehicle['damageReceivedFromInvisibles'],
          'damageReceived': vehicle['damageReceived'],
          'shots': vehicle['shots'],
          'directEnemyHits': vehicle['directEnemyHits'],
          'piercingEnemyHits': vehicle['piercingEnemyHits'],
          'explosionHits': vehicle['explosionHits'],
          'damaged': vehicle['damaged'],
          'damageDealt': vehicle['damageDealt'],
          'kills': vehicle['kills'],
          'stunned': vehicle['stunned'],
          'stunDuration': vehicle['stunDuration'],
          'piercingsReceived': vehicle['piercingsReceived'],
          'directHitsReceived': vehicle['directHitsReceived'],
          'explosionHitsReceived': vehicle['explosionHitsReceived'],
          'tankLevel': veWG.level,
          'tankTag': veWG.name,
          'tankType': short_tank_type(veWG.classTag),
          'maxHealth': vehicle['maxHealth'],
          'health': max(0, vehicle['health']),
          'isAlive': vehicle['health'] > 0
        }

      indexById = {}
      for vehicleId in vehicles:
        vehicle = vehicles[vehicleId][0]
        bdid = vehicle['accountDBID']
        if bdid not in players: continue
        player = players[bdid]
        squadID = player['prebattleID']
        res = {
          'name': player['realName'],
          'squadID': squadStorage[squadID] if squadID in squadStorage else 0,
          'bdid': bdid,
          'team': player['team'],
          'xp': vehicle['xp'],
          '__vehicleId': vehicleId
        }
        res.update(getVehicleInfo(vehicle))
        playersResultList.append(res)
        indexById[vehicleId] = len(playersResultList)

      for result in playersResultList:
        resultID = result.pop('__vehicleId')
        killerId = vehicles[resultID][0]['killerID']
        result['killerIndex'] = indexById[killerId] if killerId in indexById else -1

      avatar = results['personal']['avatar']
      personalRes = results['personal'].items()[0][1]
      killerId = personalRes['killerID']
      squadID = players[avatar['accountDBID']]['prebattleID']
      personal = {
        'team': avatar['team'],
        'xp': personalRes['originalXP'],
        'killerIndex': indexById[killerId] if killerId in indexById else -1,
        'squadID': squadStorage[squadID] if squadID in squadStorage else 0,
      }

      personal.update(getVehicleInfo(personalRes))

      battle_result = 'tie' if not winnerTeam else 'win' if winnerTeamIsMy else 'lose'
      decodeResult['playerTeam'] = playerTeam
      decodeResult['result'] = battle_result
      decodeResult['teamHealth'] = teamHealth
      decodeResult['personal'] = personal
      decodeResult['playersResults'] = playersResultList
      decodeResult['credits'] = avatar['credits']
      decodeResult['originalCredits'] = personalRes['originalCredits']
      decodeResult['duration'] = results['common']['duration']
      decodeResult['winnerTeam'] = winnerTeam
      decodeResult['arenaID'] = arenaID

      setup_session_meta(battleEvent)
      battleEvent.set_result(result=decodeResult)
      eventLogger.emit_event(battleEvent, arena_id=arenaID)

      sessionStorage.on_result_battle(result=battle_result,
                                      player_team=playerTeam,
                                      player_bdid=avatar['accountDBID'],
                                      players_results=playersResultList)

    except Exception, e:
      print_log('cannot decode battle result\n' + str(e))


onBattleResultLogger = OnBattleResultLogger()
