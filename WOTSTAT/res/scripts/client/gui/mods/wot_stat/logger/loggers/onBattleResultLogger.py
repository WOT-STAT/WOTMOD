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
        BigWorld.player().battleResultsCache.get(arenaID, lambda code, battleResults: result_callback(arenaID, code,
                                                                                                      battleResults))
      except:
        pass


  # TODO: Декодировать больше результатов
  def process_battle_result(self, results):
    arenaID = results.get('arenaUniqueID')
    print_debug("Got result for {}".format(arenaID))

    if arenaID not in self.arenas_id_wait_battle_result:
      return

    self.arenas_id_wait_battle_result.remove(arenaID)

    decodeResult = {}
    try:
      winnerTeam = results['common']['winnerTeam']
      playerTeam = results['personal']['avatar']['team']
      winnerTeamIsMy = playerTeam == winnerTeam
      teamHealth = [results['common']['teamHealth'][1], results['common']['teamHealth'][2]]

      players = results['players']
      vehicles = results['vehicles']
      playersResultList = list()

      def getVehicleInfo(vehicle):
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
        }

      for vehicleId in vehicles:
        vehicle = vehicles[vehicleId][0]
        bdid = vehicle['accountDBID']
        if bdid not in players: continue
        player = players[bdid]
        res = {
          'name': player['realName'],
          'bdid': bdid,
          'team': player['team'],
          'xp': vehicle['xp']
        }
        res.update(getVehicleInfo(vehicle))
        playersResultList.append(res)

      avatar = results['personal']['avatar']
      personalRes = results['personal'].items()[0][1]
      personal = {
        'team': avatar['team'],
        'xp': personalRes['originalXP']
      }

      personal.update(getVehicleInfo(personalRes))

      decodeResult['playerTeam'] = playerTeam
      decodeResult['result'] = 'tie' if not winnerTeam else 'win' if winnerTeamIsMy else 'lose'
      decodeResult['teamHealth'] = teamHealth
      decodeResult['personal'] = personal
      decodeResult['playersResults'] = playersResultList
      decodeResult['credits'] = avatar['credits']
      decodeResult['originalCredits'] = personalRes['originalCredits']
      decodeResult['duration'] = results['common']['duration']
      decodeResult['winnerTeam'] = winnerTeam

    except Exception, e:
      print_log('cannot decode battle result\n' + str(e))

    eventLogger.emit_event(OnBattleResult(
      result=decodeResult,
      raw=str(results)
    ), arena_id=arenaID)


onBattleResultLogger = OnBattleResultLogger()
