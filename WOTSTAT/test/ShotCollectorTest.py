# coding=utf-8
import unittest
import BigWorld
import Math

from logical.shotEventCollector import ShotEventCollector

class BaseShotTest(unittest.TestCase):
    time = 1
    def get_time(self):
        return self.time

    def skit_time(self, shotLog):
        result = None
        while self.time < 20 and not result:
            self.time += 0.1
            shotLog.append_event(None)
            result = shotLog.get_result()

        print result
        print "time: %s" % self.time
        return result

    def skit_time_to_end(self, shotLog):
        res = self.skit_time(shotLog)
        results = []
        while res:
            for r in res:
                results.append(r)
            res = self.skit_time(shotLog)
        return results

    def reset(self, name=""):
        self.time = 0
        BigWorld.serverTime = self.get_time
        print("________NEW TEST________: %s" % name)

    def assert_points(self, result, tracer_end_point, tank_hit_point, terrain_hit_point):
        self.assertEqual(result['tracer_end_point'], tracer_end_point)
        self.assertEqual(result['tank_hit_point'], tank_hit_point)
        self.assertEqual(result['terrain_hit_point'], terrain_hit_point)

    def assert_damages(self, result, damage):
        self.assertEqual(len(result['damages']), len(damage))
        for d in result['damages']:
            self.assertIn(d, damage)
            damage.remove(d)

class Basics(BaseShotTest):
    # Только show_tracer
    def test_1(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=None, tank_hit_point=None, terrain_hit_point=None)
        self.assert_damages(result, [ ])

    # Только show_tracer и hide_tracer (выстрел в скайбокс)
    def test_2(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.hide_tracer(shotID=1, point=(0, 0, 0))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(0, 0, 0), tank_hit_point=None, terrain_hit_point=None)
        self.assert_damages(result, [ ])

    # Только show_tracer, terrain_hit и hide_tracer (выстрел в землю)
    def test_3(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.hide_tracer(shotID=1, point=(0, 0, 0))
        shotLog.terrain_hit(shotID=1, point=(0, 0, 0))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(0, 0, 0), tank_hit_point=None, terrain_hit_point=(0, 0, 0))
        self.assert_damages(result, [ ])

class TankHits(BaseShotTest):
    # Рикошет от танка в землю
    def test_1(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.terrain_hit(shotID=1, point=(3, 3, 3))
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))
        shotLog.shot_result(vehicleID=1, flags=1048616)

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [ ])

    # Пробитие
    def test_2(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=1, flags=1048848)
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=200)
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [ {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': 100} ])

    # Фраг
    def test_3(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=1, flags=1048849)
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.shot_damage(vehicleID=1, newHealth=0, oldHealth=200)
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [ {'ammo_bay_destr': False, 'newHealth': 0, 'vehicleID': 1, 'damage': 200} ])

class ComplexTankHits(BaseShotTest):
    #Рикошет от рикошета
    def test_1(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=2, flags=9437280)
        shotLog.shot_result(vehicleID=1, flags=1048616)
        shotLog.shot_result(vehicleID=2, flags=9437280)
        shotLog.tank_hit(vehicleID=2, point=(3, 3, 3))
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [])

    # Урон после рикошета
    def test_2(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=2, flags=9437520)
        shotLog.shot_result(vehicleID=1, flags=1048616)
        shotLog.shot_result(vehicleID=2, flags=9437520)
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.tank_hit(vehicleID=2, point=(3, 3, 3))
        shotLog.shot_damage(vehicleID=2, newHealth=100, oldHealth=200)

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=None, tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [ {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 2, 'damage': 100} ])

class WrongEventsOrder(BaseShotTest):

    def test_1(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.shot_result(vehicleID=2, flags=9437520)
        self.time = 2.5
        shotLog.shot_result(vehicleID=2, flags=9437520)
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=1, flags=1048616)
        self.time = 2.7
        shotLog.shot_damage(vehicleID=2, newHealth=100, oldHealth=200)
        shotLog.tank_hit(vehicleID=2, point=(3, 3, 3))
        self.time = 2.8
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [ {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 2, 'damage': 100} ])

    def test_2(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.terrain_hit(shotID=1, point=(0, 0, 0))
        self.time = 2.5
        shotLog.hide_tracer(shotID=1, point=(0, 0, 0))
        self.time = 2.7
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)

        print shotLog.session_events

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(0, 0, 0), tank_hit_point=None, terrain_hit_point=(0, 0, 0))
        self.assert_damages(result, [ ])

class SPG(BaseShotTest):

    # Выстрел артой прямое + сплеш
    def test_SPG1(self):
        self.reset("SPG1")
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=1, flags=6529024)
        shotLog.shot_result(vehicleID=2, flags=5480480)
        shotLog.tank_hit(vehicleID=2, point=(2, 2, 2))
        shotLog.shot_damage(vehicleID=2, newHealth=100, oldHealth=200)
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=200)
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        result = results[0]

        self.assertEqual(len(results), 1)
        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [
            {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 2, 'damage': 100},
            {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': 100}
        ])

    # Выстрел артой сплеш по 2м, 1 фраг взрыв бк
    def test_SPG2(self):
        self.reset("SPG2")
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=5, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=1, flags=2351105)
        shotLog.shot_result(vehicleID=2, flags=5480480)
        shotLog.shot_damage(vehicleID=1, newHealth=-13, oldHealth=200)
        shotLog.tank_hit(vehicleID=2, point=(2, 2, 2))
        shotLog.shot_damage(vehicleID=2, newHealth=100, oldHealth=200)
        shotLog.hide_tracer(shotID=5, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        self.assertEqual(len(results), 1)
        result = results[0]

        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result, [
            {'ammo_bay_destr': True, 'newHealth': 0, 'vehicleID': 1, 'damage': 200},
            {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 2, 'damage': 100}
        ])

    # Выстрел артой сплеш по 2м, 1 фраг взрыв бк
    def test_SPG3(self):
        self.reset("SPG3")
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.shot_result(vehicleID=1, flags=6529024)
        shotLog.shot_result(vehicleID=2, flags=6545408)
        shotLog.terrain_hit(shotID=1, point=(2, 2, 2))
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=200)
        shotLog.shot_damage(vehicleID=2, newHealth=100, oldHealth=200)
        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))

        results = self.skit_time(shotLog)
        self.assertEqual(len(results), 1)
        result = results[0]

        self.assert_points(result, tracer_end_point=(1, 1, 1), tank_hit_point=None, terrain_hit_point=(2, 2, 2))
        self.assert_damages(result, [
            {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': 100},
            {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 2, 'damage': 100}
        ])

class MultiShots(BaseShotTest):
    def test_1(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)
        shotLog.show_tracer(shotID=2, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 1), gravity=-3, shot_click_time=0)

        shotLog.shot_result(vehicleID=1, flags=1048848)
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        shotLog.shot_result(vehicleID=1, flags=1048848)
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=200)
        shotLog.tank_hit(vehicleID=1, point=(4, 4, 4))
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=300)

        shotLog.hide_tracer(shotID=1, point=(1, 1, 1))
        shotLog.hide_tracer(shotID=2, point=(3, 3, 3))


        results = self.skit_time(shotLog)
        result1 = results[0]
        result2 = results[1]

        self.assertEqual(len(results), 2)
        self.assert_points(result1, tracer_end_point=(1, 1, 1), tank_hit_point=(2, 2, 2), terrain_hit_point=None)
        self.assert_damages(result1, [ {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': 100} ])

        self.assert_points(result2, tracer_end_point=(3, 3, 3), tank_hit_point=(4, 4, 4), terrain_hit_point=None)
        self.assert_damages(result2, [{'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': 200}])

    def test_2(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2
        shotLog.show_tracer(shotID=1, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 700), gravity=-3, shot_click_time=0)
        shotLog.show_tracer(shotID=2, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 700), gravity=-3, shot_click_time=0)
        shotLog.show_tracer(shotID=3, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 700), gravity=-3, shot_click_time=0)
        self.time = 2.1

        shotLog.hide_tracer(shotID=1, point=(-1, -1, -1))
        shotLog.hide_tracer(shotID=2, point=(-2, -2, -2))

        shotLog.tank_hit(vehicleID=1, point=(1, 1, 1))
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2))
        self.time = 2.15
        shotLog.hide_tracer(shotID=3, point=(-3, -3, -3))

        self.time = 2.2
        shotLog.tank_hit(vehicleID=1, point=(3, 3, 3))
        self.time = 2.3
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=101)
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=102)
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=103)



        self.time = 2.5
        shotLog.shot_result(vehicleID=1, flags=1048848)
        shotLog.shot_result(vehicleID=1, flags=1048848)
        shotLog.shot_result(vehicleID=1, flags=1048848)



        res = self.skit_time(shotLog)
        results = []
        while res:
            for r in res:
                results.append(r)
            res = self.skit_time(shotLog)

        for r in results:
            print r

        for r in results:
            id = -r['tracer_end_point'][0]
            self.assert_points(r, tracer_end_point=(-id, -id, -id), tank_hit_point=(id, id, id), terrain_hit_point=None)
            self.assert_damages(r, [ {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': id} ])

    def test_3(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2

        def shot(shotID):
            shotLog.show_tracer(shotID=shotID, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 700), gravity=-3, shot_click_time=0)
            shotLog.tank_hit(vehicleID=1, point=(shotID, shotID, shotID))
            shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=100 + shotID)
            self.time += 0.05
            shotLog.hide_tracer(shotID=shotID, point=(-shotID, -shotID, -shotID))

        shot(1)
        shot(2)
        shot(3)
        self.time = 2.1
        shot(4)
        shot(5)
        self.time = 2.2
        shot(6)
        self.time = 2.3
        shot(7)

        shotLog.show_tracer(shotID=8, start=Math.Vector3(0, 0, 0), velocity=Math.Vector3(0, 0, 700), gravity=-3, shot_click_time=0)

        for i in range(0, 8):
            shotLog.shot_result(1, 1048592)


        self.time += 0.1
        shotLog.tank_hit(1, point=(8, 8, 8))
        shotLog.shot_damage(vehicleID=1, newHealth=100, oldHealth=108)
        self.time += 0.1
        shotLog.hide_tracer(shotID=8, point=(-8, -8, -8))

        results = self.skit_time_to_end(shotLog)
        for r in results:
            print r

        self.assertEqual(len(results), 8)

        for r in results:
            id = -r['tracer_end_point'][0]
            self.assert_points(r, tracer_end_point=(-id, -id, -id), tank_hit_point=(id, id, id), terrain_hit_point=None)
            self.assert_damages(r, [ {'ammo_bay_destr': False, 'newHealth': 100, 'vehicleID': 1, 'damage': id} ])

    def test_4(self):
        self.reset()
        shotLog = ShotEventCollector()

        self.time = 2

        def showTracer(shotID):
            shotLog.show_tracer(shotID=shotID,start=Math.Vector3(0,0,0), velocity=Math.Vector3(0, 0, 700), gravity=-3, shot_click_time=0)

        showTracer(1) # 397470.462599 [show_tracer] shotID: 1
        self.time += 0.1
        showTracer(2) # 397470.557599 [show_tracer] shotID: 2
        shotLog.tank_hit(vehicleID=1, point=(1, 1, 1)) # 397470.557599 [tank_hit] vehicle: 1
        shotLog.shot_damage(1, 100, 101)  # 397470.557599 [shot_damage] vehicle: 1; damage: 8; kill: False; ammo_bay_destr: False; newHealth: 1557; oldHealth: 1565
        self.time += 0.04
        shotLog.hide_tracer(2, (2, 2, 2)) # 397470.585599 [hide_tracer] shotID: 2
        self.time += 0.2
        shotLog.hide_tracer(1, (1, 1, 1)) # 397470.743599 [hide_tracer] shotID: 1

        self.time += 0.01

        showTracer(3) # 397470.756599 [show_tracer] shotID: 3
        self.time += 0.2
        showTracer(4) # 397470.960599 [show_tracer] shotID: 4
        shotLog.tank_hit(vehicleID=1, point=(2, 2, 2)) # 397470.960599 [tank_hit] vehicle: 1
        shotLog.shot_damage(1, 100, 102) # 397470.960599 [shot_damage] vehicle: 1; damage: 9; kill: False; ammo_bay_destr: False; newHealth: 1548; oldHealth: 1557
        self.time += 0.03
        shotLog.hide_tracer(4, (4, 4, 4)) # 397470.984599 [hide_tracer] shotID: 4
        self.time += 0.1
        shotLog.hide_tracer(3, (3, 3, 3)) # 397471.036599 [hide_tracer] shotID: 3

        self.time += 0.1
        showTracer(5) # 397471.163599 [show_tracer] shotID: 5
        shotLog.tank_hit(vehicleID=1, point=(3, 3, 3)) # 397471.163599 [tank_hit] vehicle: 1
        shotLog.shot_damage(1, 100, 103) # 397471.163599 [shot_damage] vehicle: 1; damage: 7; kill: False; ammo_bay_destr: False; newHealth: 1541; oldHealth: 1548
        self.time += 0.02
        shotLog.hide_tracer(5, (5, 5, 5)) # 397471.182599 [hide_tracer] shotID: 5

        self.time += 0.2
        showTracer(6) # 397471.356599 [show_tracer] shotID: 6
        self.time += 0.2
        showTracer(7) # 397471.558599 [show_tracer] shotID: 7
        self.time += 0.1
        shotLog.hide_tracer(6, (6, 6, 6)) # 397471.636599 [hide_tracer] shotID: 6
        self.time += 0.1
        showTracer(8) # 397471.758599 [show_tracer] shotID: 8
        shotLog.tank_hit(vehicleID=1, point=(4, 4, 4)) # 397471.758599 [tank_hit] vehicle: 1
        shotLog.shot_damage(1, 100, 104) # 397471.758599 [shot_damage] vehicle: 1; damage: 8; kill: False; ammo_bay_destr: False; newHealth: 1533; oldHealth: 1541

        self.time += 0.02
        shotLog.hide_tracer(8, (8, 8, 8)) # 397471.784599 [hide_tracer] shotID: 8
        self.time += 0.02
        shotLog.hide_tracer(7, (7, 7, 7)) # 397471.845599 [hide_tracer] shotID: 7

        self.time += 0.1
        for i in range(0, 4): # 397471.963599
            shotLog.shot_result(1, 1048592)

        results = self.skit_time_to_end(shotLog)
        for r in results:
            print r

        self.assertEqual(len(results), 8)

        hit_count = reduce(lambda a, v: a + (v['tank_hit_point'] is not None), results, 0)
        self.assertEqual(hit_count, 4)



if __name__ == '__main__':
    unittest.main()
