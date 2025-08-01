# Python stubs generated by omniidl from GameService.idl
# DO NOT EDIT THIS FILE!

import omniORB, _omnipy
from omniORB import CORBA, PortableServer
_0_CORBA = CORBA


_omnipy.checkVersion(4,2, __file__, 1)

try:
    property
except NameError:
    def property(*args):
        return None


#
# Start of module "service"
#
__name__ = "service"
_0_service = omniORB.openModule("service", r"GameService.idl")
_0_service__POA = omniORB.openModule("service__POA", r"GameService.idl")


# struct GameSession
_0_service.GameSession = omniORB.newEmptyClass()
class GameSession (omniORB.StructBase):
    _NP_RepositoryId = "IDL:service/GameSession:1.0"

    def __init__(self, gameId, startTime, playerUsernames, sessionStatus):
        self.gameId = gameId
        self.startTime = startTime
        self.playerUsernames = playerUsernames
        self.sessionStatus = sessionStatus

_0_service.GameSession = GameSession
_0_service._d_GameSession  = (omniORB.tcInternal.tv_struct, GameSession, GameSession._NP_RepositoryId, "GameSession", "gameId", (omniORB.tcInternal.tv_string,0), "startTime", (omniORB.tcInternal.tv_string,0), "playerUsernames", (omniORB.tcInternal.tv_sequence, (omniORB.tcInternal.tv_string,0), 0), "sessionStatus", (omniORB.tcInternal.tv_string,0))
_0_service._tc_GameSession = omniORB.tcInternal.createTypeCode(_0_service._d_GameSession)
omniORB.registerType(GameSession._NP_RepositoryId, _0_service._d_GameSession, _0_service._tc_GameSession)
del GameSession

# typedef ... GameSessionList
class GameSessionList:
    _NP_RepositoryId = "IDL:service/GameSessionList:1.0"
    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")
_0_service.GameSessionList = GameSessionList
_0_service._d_GameSessionList  = (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:service/GameSession:1.0"], 0)
_0_service._ad_GameSessionList = (omniORB.tcInternal.tv_alias, GameSessionList._NP_RepositoryId, "GameSessionList", (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:service/GameSession:1.0"], 0))
_0_service._tc_GameSessionList = omniORB.tcInternal.createTypeCode(_0_service._ad_GameSessionList)
omniORB.registerType(GameSessionList._NP_RepositoryId, _0_service._ad_GameSessionList, _0_service._tc_GameSessionList)
del GameSessionList

# exception NoOpponentFound
_0_service.NoOpponentFound = omniORB.newEmptyClass()
class NoOpponentFound (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/NoOpponentFound:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.NoOpponentFound = NoOpponentFound
_0_service._d_NoOpponentFound  = (omniORB.tcInternal.tv_except, NoOpponentFound, NoOpponentFound._NP_RepositoryId, "NoOpponentFound", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_NoOpponentFound = omniORB.tcInternal.createTypeCode(_0_service._d_NoOpponentFound)
omniORB.registerType(NoOpponentFound._NP_RepositoryId, _0_service._d_NoOpponentFound, _0_service._tc_NoOpponentFound)
del NoOpponentFound

# exception GameNotFound
_0_service.GameNotFound = omniORB.newEmptyClass()
class GameNotFound (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/GameNotFound:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.GameNotFound = GameNotFound
_0_service._d_GameNotFound  = (omniORB.tcInternal.tv_except, GameNotFound, GameNotFound._NP_RepositoryId, "GameNotFound", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_GameNotFound = omniORB.tcInternal.createTypeCode(_0_service._d_GameNotFound)
omniORB.registerType(GameNotFound._NP_RepositoryId, _0_service._d_GameNotFound, _0_service._tc_GameNotFound)
del GameNotFound

# exception InvalidGuess
_0_service.InvalidGuess = omniORB.newEmptyClass()
class InvalidGuess (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/InvalidGuess:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.InvalidGuess = InvalidGuess
_0_service._d_InvalidGuess  = (omniORB.tcInternal.tv_except, InvalidGuess, InvalidGuess._NP_RepositoryId, "InvalidGuess", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_InvalidGuess = omniORB.tcInternal.createTypeCode(_0_service._d_InvalidGuess)
omniORB.registerType(InvalidGuess._NP_RepositoryId, _0_service._d_InvalidGuess, _0_service._tc_InvalidGuess)
del InvalidGuess

# interface GameManagerService
_0_service._d_GameManagerService = (omniORB.tcInternal.tv_objref, "IDL:service/GameManagerService:1.0", "GameManagerService")
omniORB.typeMapping["IDL:service/GameManagerService:1.0"] = _0_service._d_GameManagerService
_0_service.GameManagerService = omniORB.newEmptyClass()
class GameManagerService :
    _NP_RepositoryId = _0_service._d_GameManagerService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_service.GameManagerService = GameManagerService
_0_service._tc_GameManagerService = omniORB.tcInternal.createTypeCode(_0_service._d_GameManagerService)
omniORB.registerType(GameManagerService._NP_RepositoryId, _0_service._d_GameManagerService, _0_service._tc_GameManagerService)

# GameManagerService operations and attributes
GameManagerService._d_joinOrCreateGameSession = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
GameManagerService._d_listActiveGameSessions = ((), (omniORB.typeMapping["IDL:service/GameSessionList:1.0"], ), None)

# GameManagerService object reference
class _objref_GameManagerService (CORBA.Object):
    _NP_RepositoryId = GameManagerService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def joinOrCreateGameSession(self, *args):
        return self._obj.invoke("joinOrCreateGameSession", _0_service.GameManagerService._d_joinOrCreateGameSession, args)

    def listActiveGameSessions(self, *args):
        return self._obj.invoke("listActiveGameSessions", _0_service.GameManagerService._d_listActiveGameSessions, args)

omniORB.registerObjref(GameManagerService._NP_RepositoryId, _objref_GameManagerService)
_0_service._objref_GameManagerService = _objref_GameManagerService
del GameManagerService, _objref_GameManagerService

# GameManagerService skeleton
__name__ = "service__POA"
class GameManagerService (PortableServer.Servant):
    _NP_RepositoryId = _0_service.GameManagerService._NP_RepositoryId


    _omni_op_d = {"joinOrCreateGameSession": _0_service.GameManagerService._d_joinOrCreateGameSession, "listActiveGameSessions": _0_service.GameManagerService._d_listActiveGameSessions}

GameManagerService._omni_skeleton = GameManagerService
_0_service__POA.GameManagerService = GameManagerService
omniORB.registerSkeleton(GameManagerService._NP_RepositoryId, GameManagerService)
del GameManagerService
__name__ = "service"

# struct WordMaskInfo
_0_service.WordMaskInfo = omniORB.newEmptyClass()
class WordMaskInfo (omniORB.StructBase):
    _NP_RepositoryId = "IDL:service/WordMaskInfo:1.0"

    def __init__(self, maskedWord, guessesLeft):
        self.maskedWord = maskedWord
        self.guessesLeft = guessesLeft

_0_service.WordMaskInfo = WordMaskInfo
_0_service._d_WordMaskInfo  = (omniORB.tcInternal.tv_struct, WordMaskInfo, WordMaskInfo._NP_RepositoryId, "WordMaskInfo", "maskedWord", (omniORB.tcInternal.tv_string,0), "guessesLeft", omniORB.tcInternal.tv_short)
_0_service._tc_WordMaskInfo = omniORB.tcInternal.createTypeCode(_0_service._d_WordMaskInfo)
omniORB.registerType(WordMaskInfo._NP_RepositoryId, _0_service._d_WordMaskInfo, _0_service._tc_WordMaskInfo)
del WordMaskInfo

# interface GameService
_0_service._d_GameService = (omniORB.tcInternal.tv_objref, "IDL:service/GameService:1.0", "GameService")
omniORB.typeMapping["IDL:service/GameService:1.0"] = _0_service._d_GameService
_0_service.GameService = omniORB.newEmptyClass()
class GameService :
    _NP_RepositoryId = _0_service._d_GameService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_service.GameService = GameService
_0_service._tc_GameService = omniORB.tcInternal.createTypeCode(_0_service._d_GameService)
omniORB.registerType(GameService._NP_RepositoryId, _0_service._d_GameService, _0_service._tc_GameService)

# GameService operations and attributes
GameService._d_requestToJoinGame = (((omniORB.tcInternal.tv_string,0), ), (), {_0_service.NoOpponentFound._NP_RepositoryId: _0_service._d_NoOpponentFound})
GameService._d_getWordMask = (((omniORB.tcInternal.tv_string,0), ), (omniORB.typeMapping["IDL:service/WordMaskInfo:1.0"], ), {_0_service.GameNotFound._NP_RepositoryId: _0_service._d_GameNotFound})
GameService._d_submitGuess = (((omniORB.tcInternal.tv_string,0), omniORB.tcInternal.tv_char), (), {_0_service.InvalidGuess._NP_RepositoryId: _0_service._d_InvalidGuess, _0_service.GameNotFound._NP_RepositoryId: _0_service._d_GameNotFound})
GameService._d_getRemainingGuesses = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_short, ), {_0_service.GameNotFound._NP_RepositoryId: _0_service._d_GameNotFound})
GameService._d_getGameStatus = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), {_0_service.GameNotFound._NP_RepositoryId: _0_service._d_GameNotFound})
GameService._d_getRoundStartTime = (((omniORB.tcInternal.tv_string,0), omniORB.tcInternal.tv_long), ((omniORB.tcInternal.tv_string,0), ), None)
GameService._d_getRoundDuration = (((omniORB.tcInternal.tv_string,0), ), (omniORB.tcInternal.tv_short, ), None)

# GameService object reference
class _objref_GameService (CORBA.Object):
    _NP_RepositoryId = GameService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def requestToJoinGame(self, *args):
        return self._obj.invoke("requestToJoinGame", _0_service.GameService._d_requestToJoinGame, args)

    def getWordMask(self, *args):
        return self._obj.invoke("getWordMask", _0_service.GameService._d_getWordMask, args)

    def submitGuess(self, *args):
        return self._obj.invoke("submitGuess", _0_service.GameService._d_submitGuess, args)

    def getRemainingGuesses(self, *args):
        return self._obj.invoke("getRemainingGuesses", _0_service.GameService._d_getRemainingGuesses, args)

    def getGameStatus(self, *args):
        return self._obj.invoke("getGameStatus", _0_service.GameService._d_getGameStatus, args)

    def getRoundStartTime(self, *args):
        return self._obj.invoke("getRoundStartTime", _0_service.GameService._d_getRoundStartTime, args)

    def getRoundDuration(self, *args):
        return self._obj.invoke("getRoundDuration", _0_service.GameService._d_getRoundDuration, args)

omniORB.registerObjref(GameService._NP_RepositoryId, _objref_GameService)
_0_service._objref_GameService = _objref_GameService
del GameService, _objref_GameService

# GameService skeleton
__name__ = "service__POA"
class GameService (PortableServer.Servant):
    _NP_RepositoryId = _0_service.GameService._NP_RepositoryId


    _omni_op_d = {"requestToJoinGame": _0_service.GameService._d_requestToJoinGame, "getWordMask": _0_service.GameService._d_getWordMask, "submitGuess": _0_service.GameService._d_submitGuess, "getRemainingGuesses": _0_service.GameService._d_getRemainingGuesses, "getGameStatus": _0_service.GameService._d_getGameStatus, "getRoundStartTime": _0_service.GameService._d_getRoundStartTime, "getRoundDuration": _0_service.GameService._d_getRoundDuration}

GameService._omni_skeleton = GameService
_0_service__POA.GameService = GameService
omniORB.registerSkeleton(GameService._NP_RepositoryId, GameService)
del GameService
__name__ = "service"

# interface WordService
_0_service._d_WordService = (omniORB.tcInternal.tv_objref, "IDL:service/WordService:1.0", "WordService")
omniORB.typeMapping["IDL:service/WordService:1.0"] = _0_service._d_WordService
_0_service.WordService = omniORB.newEmptyClass()
class WordService :
    _NP_RepositoryId = _0_service._d_WordService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_service.WordService = WordService
_0_service._tc_WordService = omniORB.tcInternal.createTypeCode(_0_service._d_WordService)
omniORB.registerType(WordService._NP_RepositoryId, _0_service._d_WordService, _0_service._tc_WordService)

# WordService operations and attributes
WordService._d_getRandomWord = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)
WordService._d_markWordAsUsed = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (), None)
WordService._d_getNewWordForNextRound = (((omniORB.tcInternal.tv_string,0), ), ((omniORB.tcInternal.tv_string,0), ), None)

# WordService object reference
class _objref_WordService (CORBA.Object):
    _NP_RepositoryId = WordService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def getRandomWord(self, *args):
        return self._obj.invoke("getRandomWord", _0_service.WordService._d_getRandomWord, args)

    def markWordAsUsed(self, *args):
        return self._obj.invoke("markWordAsUsed", _0_service.WordService._d_markWordAsUsed, args)

    def getNewWordForNextRound(self, *args):
        return self._obj.invoke("getNewWordForNextRound", _0_service.WordService._d_getNewWordForNextRound, args)

omniORB.registerObjref(WordService._NP_RepositoryId, _objref_WordService)
_0_service._objref_WordService = _objref_WordService
del WordService, _objref_WordService

# WordService skeleton
__name__ = "service__POA"
class WordService (PortableServer.Servant):
    _NP_RepositoryId = _0_service.WordService._NP_RepositoryId


    _omni_op_d = {"getRandomWord": _0_service.WordService._d_getRandomWord, "markWordAsUsed": _0_service.WordService._d_markWordAsUsed, "getNewWordForNextRound": _0_service.WordService._d_getNewWordForNextRound}

WordService._omni_skeleton = WordService
_0_service__POA.WordService = WordService
omniORB.registerSkeleton(WordService._NP_RepositoryId, WordService)
del WordService
__name__ = "service"

#
# End of module "service"
#
__name__ = "GameService_idl"

_exported_modules = ( "service", )

# The end.
