import BigWorld

from Avatar import PlayerAvatar
from VehicleGunRotator import VehicleGunRotator
from ProjectileMover import ProjectileMover
from Vehicle import Vehicle

from ..common.hook import g_overrideLib


class WotHookEvents:
    listeners = {}

    def __init__(self):
        self.listeners = {}

    def add_listener(self, name, callback):
        if name not in self.listeners:
            self.listeners[name] = []
        self.listeners[name].append(callback)

    def remove_listener(self, name, callback):
        if name in self.listeners:
            self.listeners = filter(lambda t: t != callback, self.listeners)

    def invoke(self, name, obj, *a, **k):
        if name in self.listeners:
            for f in self.listeners[name]:
                f(obj, *a, **k)


wotHookEvents = WotHookEvents()


# ------------------INIT------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'onEnterWorld')
def onEnterWorld(self, *a, **k):
    wotHookEvents.invoke('PlayerAvatar.onEnterWorld', self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'updateTargetingInfo')
def updateTargetingInfo(self, *a, **k):
    wotHookEvents.invoke('PlayerAvatar.updateTargetingInfo', self, *a, **k)


# -------------------MOVE------------------#

@g_overrideLib.registerEvent(VehicleGunRotator, 'setShotPosition')
def setShotPosition(self, *a, **k):
    wotHookEvents.invoke('VehicleGunRotator.setShotPosition', self, *a, **k)


@g_overrideLib.registerEvent(VehicleGunRotator, '_VehicleGunRotator__updateGunMarker')
def updateGunMarker(self, *a, **k):
    wotHookEvents.invoke('VehicleGunRotator.updateGunMarker', self, *a, **k)


# -------------------SHOT------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'shoot')
def shoot(self, *a, **k):
    wotHookEvents.invoke('PlayerAvatar.shoot', self, *a, **k)


@g_overrideLib.registerEvent(PlayerAvatar, 'showTracer')
def showTracer(self, *a, **k):
    wotHookEvents.invoke('PlayerAvatar.showTracer', self, *a, **k)


# -------------------EXPLOSION------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'explodeProjectile')
def explodeProjectile(self, *a, **k):
    wotHookEvents.invoke('PlayerAvatar.explodeProjectile', self, *a, **k)


@g_overrideLib.registerEvent(Vehicle, 'showDamageFromShot')
def showDamageFromShot(self, *a, **k):
    wotHookEvents.invoke('Vehicle.showDamageFromShot', self, *a, **k)

# -------------------PROJECTILE-------------------#

@g_overrideLib.registerEvent(ProjectileMover, '_ProjectileMover__killProjectile')
def killProjectile(self, *a, **k):
    wotHookEvents.invoke('ProjectileMover.killProjectile', self, *a, **k)


# -------------------HELP-------------------#

@g_overrideLib.registerEvent(PlayerAvatar, 'enableServerAim')
def enableServerAim(self, *a, **k):
    wotHookEvents.invoke('PlayerAvatar.enableServerAim', self, *a, **k)

