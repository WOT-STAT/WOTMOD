import BigWorld

from Avatar import PlayerAvatar
from VehicleGunRotator import VehicleGunRotator
from ProjectileMover import ProjectileMover
from Vehicle import Vehicle
import Event

from ..common.hook import g_overrideLib


class WotHookEvents:
  def __init__(self):
    self.listeners = {}
    # ------------------INIT------------------#
    self.PlayerAvatar_onEnterWorld = Event.Event()
    self.PlayerAvatar_updateTargetingInfo = Event.Event()
    self.PlayerAvatar_onArenaPeriodChange = Event.Event()
    # -------------------MOVE------------------#
    self.VehicleGunRotator_setShotPosition = Event.Event()
    self.VehicleGunRotator_updateGunMarker = Event.Event()
    # -------------------SHOT------------------#
    self.PlayerAvatar_shoot = Event.Event()
    self.PlayerAvatar_showTracer = Event.Event()
    self.PlayerAvatar_showShotResults = Event.Event()
    self.Vehicle_onHealthChanged = Event.Event()
    self.PlayerAvatar_showOwnVehicleHitDirection = Event.Event()
    # -------------------EXPLOSION------------------#
    self.PlayerAvatar_explodeProjectile = Event.Event()
    self.Vehicle_showDamageFromShot = Event.Event()
    # -------------------PROJECTILE-------------------#
    self.ProjectileMover_killProjectile = Event.Event()
    # -------------------HELP-------------------#
    self.PlayerAvatar_enableServerAim = Event.Event()


wotHookEvents = WotHookEvents()


# ------------------INIT------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'onEnterWorld')
def onEnterWorld(self, *a, **k):
  wotHookEvents.PlayerAvatar_onEnterWorld(self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'updateTargetingInfo')
def updateTargetingInfo(self, *a, **k):
  wotHookEvents.PlayerAvatar_updateTargetingInfo(self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, '_PlayerAvatar__onArenaPeriodChange')
def onArenaPeriodChange(self, *a, **k):
  wotHookEvents.PlayerAvatar_onArenaPeriodChange(self, *a, **k)


# -------------------MOVE------------------#

@g_overrideLib.registerEvent(VehicleGunRotator, 'setShotPosition')
def setShotPosition(self, *a, **k):
  wotHookEvents.VehicleGunRotator_setShotPosition(self, *a, **k)


@g_overrideLib.registerEvent(VehicleGunRotator, '_VehicleGunRotator__updateGunMarker')
def updateGunMarker(self, *a, **k):
  wotHookEvents.VehicleGunRotator_updateGunMarker(self, *a, **k)


# -------------------SHOT------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'shoot')
def shoot(self, *a, **k):
  wotHookEvents.PlayerAvatar_shoot(self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'showTracer')
def showTracer(self, *a, **k):
  wotHookEvents.PlayerAvatar_showTracer(self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'showShotResults')
def showShotResults(self, *a, **k):
  wotHookEvents.PlayerAvatar_showShotResults(self, *a, **k)


@g_overrideLib.registerEvent(Vehicle, 'onHealthChanged')
def onHealthChanged(self, *a, **k):
  wotHookEvents.Vehicle_onHealthChanged(self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'showOwnVehicleHitDirection')
def showOwnVehicleHitDirection(self, *a, **k):
  wotHookEvents.PlayerAvatar_showOwnVehicleHitDirection(self, *a, **k)


# -------------------EXPLOSION------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'explodeProjectile')
def explodeProjectile(self, *a, **k):
  wotHookEvents.PlayerAvatar_explodeProjectile(self, *a, **k)


@g_overrideLib.registerEvent(Vehicle, 'showDamageFromShot')
def showDamageFromShot(self, *a, **k):
  wotHookEvents.Vehicle_showDamageFromShot(self, *a, **k)


# -------------------PROJECTILE-------------------#

@g_overrideLib.registerEvent(ProjectileMover, '_ProjectileMover__killProjectile')
def killProjectile(self, *a, **k):
  wotHookEvents.ProjectileMover_killProjectile(self, *a, **k)


# -------------------HELP-------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'enableServerAim')
def enableServerAim(self, *a, **k):
  wotHookEvents.PlayerAvatar_enableServerAim(self, *a, **k)
