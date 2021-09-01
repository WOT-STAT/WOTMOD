import BigWorld

from constants import ARENA_BONUS_TYPE


def vector(t): return {'x': t.x, 'y': t.y, 'z': t.z} if t else None


arenaTags = dict(
    [(v, k) for k, v in ARENA_BONUS_TYPE.__dict__.iteritems() if isinstance(v, int)])


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

