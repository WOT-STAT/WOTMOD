# coding=utf-8
import BattleReplay
import BigWorld
from Math import Matrix
from VehicleEffects import DamageFromShotDecoder
from constants import SERVER_TICK_LENGTH

from ..eventLogger import eventLogger, battle_time
from ..events import OnShot
from ..utils import vector, own_gun_position
from ..wotHookEvents import wotHookEvents
from ...utils import print_log, print_debug


def own_effect_index(player):
    return map(lambda t: t.shell.effectsIndex, player.vehicleTypeDescriptor.gun.shots)


class OnShotLogger:
    shots_order = []
    shots_list = dict()

    marker_server_pos = None
    marker_server_disp = None
    marker_client_pos = None
    marker_client_disp = None

    temp_shot = OnShot()

    def __init__(self):
        wotHookEvents.VehicleGunRotator_updateGunMarker += self.update_gun_marker_client
        wotHookEvents.VehicleGunRotator_setShotPosition += self.update_gun_marker_server
        wotHookEvents.PlayerAvatar_shoot += self.shoot
        wotHookEvents.PlayerAvatar_showTracer += self.show_tracer
        wotHookEvents.Vehicle_showDamageFromShot += self.show_damage_from_shot
        wotHookEvents.PlayerAvatar_explodeProjectile += self.explode_projectile
        wotHookEvents.ProjectileMover_killProjectile += self.kill_projectile

    def update_gun_marker_server(self, obj, vehicleID, shotPos, shotVec, dispersionAngle, *a, **k):
        self.marker_server_pos = obj._VehicleGunRotator__getGunMarkerPosition(
            shotPos, shotVec, (dispersionAngle, dispersionAngle))[0]
        self.marker_server_disp = dispersionAngle

    def update_gun_marker_client(self, obj, *a, **k):
        shotPos, shotVec = obj.getCurShotPosition()
        self.marker_client_pos = obj._VehicleGunRotator__getGunMarkerPosition(
            shotPos, shotVec, obj._VehicleGunRotator__dispersionAngles)[0]

        self.marker_client_disp = obj._VehicleGunRotator__dispersionAngles[0]

    def shoot(self, obj, isRepeat=False, *a, **k):
        can_shoot, error = obj.guiSessionProvider.shared.ammo.canShoot(isRepeat)
        if not can_shoot:
            return

        player = BigWorld.player()
        self.temp_shot.set_battle_time(battle_time())
        self.temp_shot.set_date()
        self.temp_shot.set_server_marker(vector(self.marker_server_pos), self.marker_server_disp)
        self.temp_shot.set_client_marker(vector(self.marker_client_pos), self.marker_client_disp)
        shot = player.vehicleTypeDescriptor.shot
        self.temp_shot.set_shoot(gun_position=vector(own_gun_position(player)),
                                 battle_dispersion=player.vehicleTypeDescriptor.gun.shotDispersionAngle,
                                 shot_dispersion=(
                                         player.vehicleTypeDescriptor.gun.shotDispersionAngle *
                                         player._PlayerAvatar__aimingInfo[2]),
                                 shell_name=player.vehicleTypeDescriptor.shot.shell.name,
                                 shell_tag=player.vehicleTypeDescriptor.shot.shell.kind,
                                 damage=str(shot.shell.damage),
                                 caliber=shot.shell.caliber,
                                 piercingPower=str(shot.piercingPower),
                                 speed=shot.speed / 0.8,
                                 maxDistance=shot.maxDistance,
                                 ping=BigWorld.LatencyInfo().value[3] - 0.5 * SERVER_TICK_LENGTH,
                                 auto_aim=(player.autoAimVehicle is not None),
                                 server_aim=bool(player.gunRotator.settingsCore.getSetting('useServerAim'))
                                 )

    def show_tracer(self, obj, attackerID, shotID, isRicochet, effectsIndex, refStartPoint, refVelocity, gravity, *a,
                    **k):

        player = BigWorld.player()
        if isRicochet or attackerID != player.playerVehicleID or effectsIndex not in own_effect_index(player):
            return

        self.temp_shot.set_tracer(shot_id=shotID, start=vector(refStartPoint), velocity=vector(refVelocity / 0.8),
                                  gravity=gravity / 0.64)
        self.shots_order.append(shotID)
        self.shots_list[shotID] = self.temp_shot
        self.temp_shot = OnShot()

    def explode_projectile(self, obj, shotID, effectsIndex, effectMaterialIndex, endPoint, *a, **k):
        if effectsIndex not in own_effect_index(BigWorld.player()):
            return

        if shotID in self.shots_list:
            self.shots_list[shotID].set_hit(vector(endPoint), 'terrain')

    def show_damage_from_shot(self, obj, attackerID, points, effectsIndex, *a, **k):
        player = BigWorld.player()

        if len(self.shots_order) == 0 or attackerID != player.playerVehicleID or effectsIndex not in own_effect_index(player):
            return

        decodedPoints = DamageFromShotDecoder.decodeHitPoints(points, obj.appearance.collisions)
        if not decodedPoints:
            return

        firstHitPoint = decodedPoints[0]
        compMatrix = Matrix(obj.appearance.compoundModel.node(firstHitPoint.componentName))
        firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
        firstHitDir = compMatrix.applyVector(firstHitDirLocal)
        firstHitDir.normalise()
        firstHitPos = compMatrix.applyPoint(firstHitPoint.matrix.translation)

        shot = self.shots_list[self.shots_order[0]]
        shot.set_hit(vector(firstHitPos), 'tank')

    def kill_projectile(self, obj, shotID, position, impactVelDir, deathType, *a, **k):
        if abs(shotID) in self.shots_order:
            self.shots_order.remove(abs(shotID))
            shot = self.shots_list.pop(abs(shotID))  # type: OnShot
            eventLogger.emit_event(shot.set_tracer_end(vector(position)))


onShotLogger = OnShotLogger()
