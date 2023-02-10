from functools import partial

import BattleReplay
import BigWorld
from PlayerEvents import g_playerEvents
from ..eventLogger import eventLogger
from ..events import OnBattleResult
from ...utils import print_log, print_debug


class OnBattleResultLogger:
    arenas_id_wait_battle_result = []
    battle_loaded = False

    def __init__(self):
        self.arenas_id_wait_battle_result = []
        self.battle_loaded = False

        g_playerEvents.onBattleResultsReceived += self.on_battle_results_received
        eventLogger.on_session_created += self.on_session_created
        self.battle_result_cache_checker()

    def on_session_created(self, battleEventSession):
        self.arenas_id_wait_battle_result.append(battleEventSession.arenaID)

    def on_battle_results_received(self, isPlayerVehicle, results):
        if not isPlayerVehicle or BattleReplay.isPlaying():
            return
        self.process_battle_result(results)

    def battle_result_cache_checker(self):
        BigWorld.callback(3, self.battle_result_cache_checker)

        def result_callback(arenaID, code, result):
            if code > 0:
                self.process_battle_result(result)

        if len(self.arenas_id_wait_battle_result) > 0:
            arenaID = self.arenas_id_wait_battle_result.pop(0)
            self.arenas_id_wait_battle_result.append(arenaID)
            try:
                BigWorld.player().battleResultsCache.get(arenaID, partial(result_callback, arenaID))
            except:
                pass


    # TODO: Декодировать больше результатов
    def process_battle_result(self, results):

        arenaID = results.get('arenaUniqueID')
        if arenaID not in self.arenas_id_wait_battle_result:
            return

        self.arenas_id_wait_battle_result.remove(arenaID)

        decodeResult = {}
        try:
            decodeResult['res'] = 'win' if results['personal']['avatar']['team'] == results['common'][
                'winnerTeam'] else 'lose'
            decodeResult['xp'] = results['personal']['avatar']['xp']
            decodeResult['credits'] = results['personal']['avatar']['credits']
            decodeResult['duration'] = results['common']['duration']
            decodeResult['bots_count'] = len(results['common']['bots'])
        except Exception, e:
            print_log('cannot decode battle result\n' + str(e))

        eventLogger.emit_event(OnBattleResult(
            Result=decodeResult.get('res'),
            Credits=decodeResult.get('credits'),
            XP=decodeResult.get('xp'),
            Duration=decodeResult.get('duration')*1000,
            BotsCount=decodeResult.get('bots_count')
        ), arena_id=arenaID)


onBattleResultLogger = OnBattleResultLogger()