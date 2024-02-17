import BigWorld
import re
from BattleFeedbackCommon import BATTLE_EVENT_TYPE

from constants import ARENA_BONUS_TYPE, ARENA_GAMEPLAY_NAMES, AUTH_REALM
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from vehicle_systems.tankStructure import TankPartNames
from account_shared import readClientServerVersion
from ..load_mod import config


def vector(t): return {'x': t.x, 'y': t.y, 'z': t.z} if t else None


def own_gun_position(player=BigWorld.player()):
  if player.vehicle and player.vehicle.isStarted and player.vehicle.appearance:
    return player.vehicle.appearance.compoundModel.node(TankPartNames.GUN).position
  else:
    return player.getOwnVehiclePosition() + \
           player.vehicleTypeDescriptor.hull.turretPositions[0] + \
           player.vehicleTypeDescriptor.turret.gunPosition


ARENA_TAGS = dict(
  [(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])

FEEDBACK_EVENT = dict([(v, k) for k, v in FEEDBACK_EVENT_ID.__dict__.iteritems() if isinstance(v, int)])
BATTLE_EVENT = dict([(v, k) for k, v in BATTLE_EVENT_TYPE.__dict__.iteritems() if isinstance(v, int)])

GAME_VERSION = readClientServerVersion()[1]


def short_tank_type(tag):
  tags = {
    'lightTank': 'LT',
    'mediumTank': 'MT',
    'heavyTank': 'HT',
    'AT-SPG': 'AT',
    'SPG': 'SPG',
  }
  return tags[tag] if tag in tags else tag


def get_tank_type(vehicleTags):
  tags = vehicleTags
  res = 'mediumTank' if 'mediumTank' in tags \
    else 'heavyTank' if 'heavyTank' in tags \
    else 'AT-SPG' if 'AT-SPG' in tags \
    else 'SPG' if 'SPG' in tags \
    else 'lightTank' if 'lightTank' in tags \
    else 'None'
  return res


def setup_dynamic_battle_info(dynamicBattleEvent):
  """
  @type dynamicBattleEvent: DynamicBattleEvent
  """
  player = BigWorld.player()
  serverName = player.connectionMgr.serverUserName
  if config.get('hideServer'):
    serverName = re.sub(r'\d+', '_hide_', serverName)

  dynamicBattleEvent.setupDynamicBattleInfo(
    arenaTag=player.arena.arenaType.geometry,
    playerName=player.name,
    playerClan=player.arena.vehicles[player.playerVehicleID]['clanAbbrev'],
    accountDBID=player.arena.vehicles[player.playerVehicleID]['accountDBID'],
    battleMode=ARENA_TAGS[player.arena.bonusType],
    battleGameplay=ARENA_GAMEPLAY_NAMES[player.arenaTypeID >> 16],
    serverName=serverName,
    region=AUTH_REALM,
    gameVersion=GAME_VERSION,
    modVersion=config.get('version'),
    team=player.team,
    tankTag=BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.name,
    tankType=short_tank_type(get_tank_type(player.vehicleTypeDescriptor.type.tags)),
    tankLevel=player.vehicleTypeDescriptor.level,
    gunTag=player.vehicleTypeDescriptor.gun.name
  )
  pass
