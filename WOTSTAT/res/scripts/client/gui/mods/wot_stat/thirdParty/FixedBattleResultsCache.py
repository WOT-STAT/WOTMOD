# SPDX-License-Identifier: MIT
# Copyright (c) 2019-2024 Andrii Andrushchyshyn

import BigWorld
import cPickle
import functools
import zlib
import AccountCommands
from account_helpers import BattleResultsCache
from debug_utils import LOG_CURRENT_EXCEPTION

class FixedBattleResultsCache(object):

	# backward compatibility
	fix_version = 1.8

	def __init__(self):
		self.__account = None
		self.__ignore = True
		self.__waiting = False
		BattleResultsCache.clean()
		# locally saved battle results arenaUniqueID set
		# for request when response from server pending
		# and results already saved local
		self.__cached = set()
		# arenaUniqueID -> callback pair set
		# for request when response from server pending
		# and results not been saved local
		self.__callbacks = set()

	def onAccountBecomePlayer(self):
		self.__ignore = False
		self.__waiting = False

	def onAccountBecomeNonPlayer(self):
		self.__ignore = True
		self.__callbacks.clear()

	def setAccount(self, account):
		self.__account = account

	def get(self, arenaUniqueID, callback):
		errorCode, results = self.__checkErrorsAndGetFromCache(arenaUniqueID,
									self.__account.name)
		if errorCode in (AccountCommands.RES_CACHE, AccountCommands.RES_NON_PLAYER):
			if callback is not None:
				callback(errorCode, results)
			return
		self.__callbacks.add((arenaUniqueID, callback, ))
		if errorCode != AccountCommands.RES_COOLDOWN:
			self.__waiting = True
			proxy = functools.partial(self.__onGetResponse, arenaUniqueID)
			# handle error when account is disconnected and onAccountBecomeNonPlayer not fired yet
			# TypeError: Entity.base is only available on the connected entity
			try:
				self.__account._doCmdInt3(AccountCommands.CMD_REQ_BATTLE_RESULTS,
					arenaUniqueID, 0, 0, proxy)
			except TypeError:
				self.__waiting = False
				self.__callbacks.remove((arenaUniqueID, callback, ))
				callback(AccountCommands.RES_FAILURE, None)
			return

	def getOther(self, arenaUniqueID, resultsSubUrl, callback):
		(errorCode, results) = self.__checkErrorsAndGetFromCache(arenaUniqueID,
									resultsSubUrl)
		if errorCode is not None:
			if callback is not None:
				callback(errorCode, results)
			return
		else:
			raise NotImplementedError

	def __checkErrorsAndGetFromCache(self, arenaUniqueID, uniqueFolderName):
		if self.__ignore:
			return (AccountCommands.RES_NON_PLAYER, None)
		# in case we revive the response from the server
		# but the requested battle results is already available
		elif arenaUniqueID in self.__cached:
			return self.__getFromCache(arenaUniqueID, uniqueFolderName)
		elif self.__waiting:
			return (AccountCommands.RES_COOLDOWN, None)
		else:
			return self.__getFromCache(arenaUniqueID, uniqueFolderName)

	def __getFromCache(self, arenaUniqueID, uniqueFolderName):
		battleResults = BattleResultsCache.load(uniqueFolderName, arenaUniqueID)
		if battleResults is None:
			return (None, None)
		# flag this battle as a locally available one
		self.__cached.add(arenaUniqueID)
		converted = BattleResultsCache.convertToFullForm(battleResults)
		return (AccountCommands.RES_CACHE, converted)

	def __onGetResponse(self, arenaUniqueID, requestID, resultID, errorStr, ext=None):
		if resultID == AccountCommands.RES_STREAM:
			proxy = functools.partial(self.__onStreamComplete, arenaUniqueID)
			self.__account._subscribeForStream(requestID, proxy)
		else:
			self.__finalizeResponse(arenaUniqueID, (resultID, None))

	def __onStreamComplete(self, arenaUniqueID, isSuccess, data):
		try:
			# cheeck for broken Stream 
			# on Account destroy/leave lobby
			if isSuccess:
				battleResults = cPickle.loads(zlib.decompress(data))
				BattleResultsCache.save(self.__account.name, battleResults)
				converted = BattleResultsCache.convertToFullForm(battleResults)
				response = (AccountCommands.RES_STREAM, converted)
				self.__account.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE,
						AccountCommands.CMD_BATTLE_RESULTS_RECEIVED,
						arenaUniqueID, 0, 0)
				# flag this battle as a locally available one
				self.__cached.add(arenaUniqueID)
			else:
				# we got broken Stream
				# set response result to RES_FAILURE 
				response = (AccountCommands.RES_FAILURE, None)
		except Exception:
			LOG_CURRENT_EXCEPTION()
			# we got problems in Stream data parsing/saving
			# set response result to RES_FAILURE 
			response = (AccountCommands.RES_FAILURE, None)
		self.__finalizeResponse(arenaUniqueID, response)

	def __finalizeResponse(self, arenaUniqueID, data):
		self.__waiting = False
		for (_arenaUniqueID, callback, ) in self.__callbacks.copy():
			if _arenaUniqueID == arenaUniqueID:
				try:
					callback(*data)
				except Exception:
					LOG_CURRENT_EXCEPTION()
				finally:
					self.__callbacks.remove((_arenaUniqueID, callback, ))
			else:
				# revive requests at the next frame
				proxy = functools.partial(self.get, _arenaUniqueID, callback)
				BigWorld.callback(.0, proxy)


def setup():
  if hasattr(BattleResultsCache.BattleResultsCache, 'fix_version'): 
    return 'Already injected: %s' % str(BattleResultsCache.BattleResultsCache.fix_version)
  else:
    BattleResultsCache.BattleResultsCache = FixedBattleResultsCache
    return 'Injected'
