import BigWorld
from BattleFeedbackCommon import BATTLE_EVENT_TYPE

from constants import ARENA_BONUS_TYPE
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from vehicle_systems.tankStructure import TankPartNames


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
