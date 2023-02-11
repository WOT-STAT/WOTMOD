import BigWorld
from VehicleEffects import DamageFromShotDecoder
from constants import ATTACK_REASON_INDICES, ATTACK_REASON
from ..wotHookEvents import wotHookEvents
from ...utils import print_debug


class OnShotReceiveLogger:
  def __init__(self):
    wotHookEvents.Vehicle_showDamageFromShot += self.show_damage_from_shot
    wotHookEvents.Vehicle_onHealthChanged += self.on_health_changed
    wotHookEvents.PlayerAvatar_showOwnVehicleHitDirection += self.showOwnVehicleHitDirection

  def on_health_changed(self, obj, newHealth, oldHealth, attackerID, attackReasonID):
    if obj.id == BigWorld.player().playerVehicleID and BigWorld.player().arena.vehicles[attackerID][
      'team'] != BigWorld.player().team:
      print_debug("________on_health_changed: %s" % newHealth)

  def show_damage_from_shot(self, obj, attackerID, points, effectsIndex, *a, **k):
    player = BigWorld.player()

    if attackerID == player.playerVehicleID or BigWorld.player().arena.vehicles[attackerID][
      'team'] == BigWorld.player().team:
      return

    print_debug(
      "__________show_damage_from_shot: %s" % BigWorld.player().arena.vehicles[attackerID]['vehicleType'].name)

  def showOwnVehicleHitDirection(self, obj, hitDirYaw, attackerID, damage, crits, isBlocked, isShellHE, damagedID,
                                 attackReasonID):
    if BigWorld.player().arena.vehicles[attackerID]['team'] != BigWorld.player().team:
      print_debug(
        "showOwnVehicleHitDirection: damage: %s\ncrits: %s\nisBlocked: %s\nisShellHE: %s\ndamagedID: %s\nattackReasonID: %s" % (
          damage, crits, isBlocked, isShellHE, damagedID, attackReasonID))


onShotReceiveLogger = OnShotReceiveLogger()
