# Python stubs generated by omniidl from UserService.idl
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
_0_service = omniORB.openModule("service", r"UserService.idl")
_0_service__POA = omniORB.openModule("service__POA", r"UserService.idl")


# exception AlreadyExists
_0_service.AlreadyExists = omniORB.newEmptyClass()
class AlreadyExists (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/AlreadyExists:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.AlreadyExists = AlreadyExists
_0_service._d_AlreadyExists  = (omniORB.tcInternal.tv_except, AlreadyExists, AlreadyExists._NP_RepositoryId, "AlreadyExists", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_AlreadyExists = omniORB.tcInternal.createTypeCode(_0_service._d_AlreadyExists)
omniORB.registerType(AlreadyExists._NP_RepositoryId, _0_service._d_AlreadyExists, _0_service._tc_AlreadyExists)
del AlreadyExists

# exception NotFound
_0_service.NotFound = omniORB.newEmptyClass()
class NotFound (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/NotFound:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.NotFound = NotFound
_0_service._d_NotFound  = (omniORB.tcInternal.tv_except, NotFound, NotFound._NP_RepositoryId, "NotFound", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_NotFound = omniORB.tcInternal.createTypeCode(_0_service._d_NotFound)
omniORB.registerType(NotFound._NP_RepositoryId, _0_service._d_NotFound, _0_service._tc_NotFound)
del NotFound

# exception InvalidCredentials
_0_service.InvalidCredentials = omniORB.newEmptyClass()
class InvalidCredentials (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/InvalidCredentials:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.InvalidCredentials = InvalidCredentials
_0_service._d_InvalidCredentials  = (omniORB.tcInternal.tv_except, InvalidCredentials, InvalidCredentials._NP_RepositoryId, "InvalidCredentials", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_InvalidCredentials = omniORB.tcInternal.createTypeCode(_0_service._d_InvalidCredentials)
omniORB.registerType(InvalidCredentials._NP_RepositoryId, _0_service._d_InvalidCredentials, _0_service._tc_InvalidCredentials)
del InvalidCredentials

# exception AlreadyLoggedIn
_0_service.AlreadyLoggedIn = omniORB.newEmptyClass()
class AlreadyLoggedIn (CORBA.UserException):
    _NP_RepositoryId = "IDL:service/AlreadyLoggedIn:1.0"

    def __init__(self, reason):
        CORBA.UserException.__init__(self, reason)
        self.reason = reason

_0_service.AlreadyLoggedIn = AlreadyLoggedIn
_0_service._d_AlreadyLoggedIn  = (omniORB.tcInternal.tv_except, AlreadyLoggedIn, AlreadyLoggedIn._NP_RepositoryId, "AlreadyLoggedIn", "reason", (omniORB.tcInternal.tv_string,0))
_0_service._tc_AlreadyLoggedIn = omniORB.tcInternal.createTypeCode(_0_service._d_AlreadyLoggedIn)
omniORB.registerType(AlreadyLoggedIn._NP_RepositoryId, _0_service._d_AlreadyLoggedIn, _0_service._tc_AlreadyLoggedIn)
del AlreadyLoggedIn

# struct PlayerAccount
_0_service.PlayerAccount = omniORB.newEmptyClass()
class PlayerAccount (omniORB.StructBase):
    _NP_RepositoryId = "IDL:service/PlayerAccount:1.0"

    def __init__(self, playerId, username, password, wins, isLoggedIn):
        self.playerId = playerId
        self.username = username
        self.password = password
        self.wins = wins
        self.isLoggedIn = isLoggedIn

_0_service.PlayerAccount = PlayerAccount
_0_service._d_PlayerAccount  = (omniORB.tcInternal.tv_struct, PlayerAccount, PlayerAccount._NP_RepositoryId, "PlayerAccount", "playerId", omniORB.tcInternal.tv_long, "username", (omniORB.tcInternal.tv_string,0), "password", (omniORB.tcInternal.tv_string,0), "wins", omniORB.tcInternal.tv_short, "isLoggedIn", omniORB.tcInternal.tv_boolean)
_0_service._tc_PlayerAccount = omniORB.tcInternal.createTypeCode(_0_service._d_PlayerAccount)
omniORB.registerType(PlayerAccount._NP_RepositoryId, _0_service._d_PlayerAccount, _0_service._tc_PlayerAccount)
del PlayerAccount

# typedef ... PlayerList
class PlayerList:
    _NP_RepositoryId = "IDL:service/PlayerList:1.0"
    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")
_0_service.PlayerList = PlayerList
_0_service._d_PlayerList  = (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:service/PlayerAccount:1.0"], 0)
_0_service._ad_PlayerList = (omniORB.tcInternal.tv_alias, PlayerList._NP_RepositoryId, "PlayerList", (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:service/PlayerAccount:1.0"], 0))
_0_service._tc_PlayerList = omniORB.tcInternal.createTypeCode(_0_service._ad_PlayerList)
omniORB.registerType(PlayerList._NP_RepositoryId, _0_service._ad_PlayerList, _0_service._tc_PlayerList)
del PlayerList

# struct GameConfiguration
_0_service.GameConfiguration = omniORB.newEmptyClass()
class GameConfiguration (omniORB.StructBase):
    _NP_RepositoryId = "IDL:service/GameConfiguration:1.0"

    def __init__(self, waitTimeInSeconds, roundTimeInSeconds):
        self.waitTimeInSeconds = waitTimeInSeconds
        self.roundTimeInSeconds = roundTimeInSeconds

_0_service.GameConfiguration = GameConfiguration
_0_service._d_GameConfiguration  = (omniORB.tcInternal.tv_struct, GameConfiguration, GameConfiguration._NP_RepositoryId, "GameConfiguration", "waitTimeInSeconds", omniORB.tcInternal.tv_short, "roundTimeInSeconds", omniORB.tcInternal.tv_short)
_0_service._tc_GameConfiguration = omniORB.tcInternal.createTypeCode(_0_service._d_GameConfiguration)
omniORB.registerType(GameConfiguration._NP_RepositoryId, _0_service._d_GameConfiguration, _0_service._tc_GameConfiguration)
del GameConfiguration

# interface AdminService
_0_service._d_AdminService = (omniORB.tcInternal.tv_objref, "IDL:service/AdminService:1.0", "AdminService")
omniORB.typeMapping["IDL:service/AdminService:1.0"] = _0_service._d_AdminService
_0_service.AdminService = omniORB.newEmptyClass()
class AdminService :
    _NP_RepositoryId = _0_service._d_AdminService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_service.AdminService = AdminService
_0_service._tc_AdminService = omniORB.tcInternal.createTypeCode(_0_service._d_AdminService)
omniORB.registerType(AdminService._NP_RepositoryId, _0_service._d_AdminService, _0_service._tc_AdminService)

# AdminService operations and attributes
AdminService._d_createPlayer = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (), {_0_service.AlreadyExists._NP_RepositoryId: _0_service._d_AlreadyExists})
AdminService._d_removePlayer = (((omniORB.tcInternal.tv_string,0), ), (), {_0_service.NotFound._NP_RepositoryId: _0_service._d_NotFound})
AdminService._d_updatePlayer = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (), {_0_service.NotFound._NP_RepositoryId: _0_service._d_NotFound, _0_service.AlreadyExists._NP_RepositoryId: _0_service._d_AlreadyExists})
AdminService._d_searchPlayer = (((omniORB.tcInternal.tv_string,0), ), (omniORB.typeMapping["IDL:service/PlayerList:1.0"], ), None)
AdminService._d_updateWaitTime = ((omniORB.tcInternal.tv_short, ), (), None)
AdminService._d_updateRoundTime = ((omniORB.tcInternal.tv_short, ), (), None)
AdminService._d_getWaitTime = ((), (omniORB.tcInternal.tv_short, ), None)
AdminService._d_getRoundTime = ((), (omniORB.tcInternal.tv_short, ), None)

# AdminService object reference
class _objref_AdminService (CORBA.Object):
    _NP_RepositoryId = AdminService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def createPlayer(self, *args):
        return self._obj.invoke("createPlayer", _0_service.AdminService._d_createPlayer, args)

    def removePlayer(self, *args):
        return self._obj.invoke("removePlayer", _0_service.AdminService._d_removePlayer, args)

    def updatePlayer(self, *args):
        return self._obj.invoke("updatePlayer", _0_service.AdminService._d_updatePlayer, args)

    def searchPlayer(self, *args):
        return self._obj.invoke("searchPlayer", _0_service.AdminService._d_searchPlayer, args)

    def updateWaitTime(self, *args):
        return self._obj.invoke("updateWaitTime", _0_service.AdminService._d_updateWaitTime, args)

    def updateRoundTime(self, *args):
        return self._obj.invoke("updateRoundTime", _0_service.AdminService._d_updateRoundTime, args)

    def getWaitTime(self, *args):
        return self._obj.invoke("getWaitTime", _0_service.AdminService._d_getWaitTime, args)

    def getRoundTime(self, *args):
        return self._obj.invoke("getRoundTime", _0_service.AdminService._d_getRoundTime, args)

omniORB.registerObjref(AdminService._NP_RepositoryId, _objref_AdminService)
_0_service._objref_AdminService = _objref_AdminService
del AdminService, _objref_AdminService

# AdminService skeleton
__name__ = "service__POA"
class AdminService (PortableServer.Servant):
    _NP_RepositoryId = _0_service.AdminService._NP_RepositoryId


    _omni_op_d = {"createPlayer": _0_service.AdminService._d_createPlayer, "removePlayer": _0_service.AdminService._d_removePlayer, "updatePlayer": _0_service.AdminService._d_updatePlayer, "searchPlayer": _0_service.AdminService._d_searchPlayer, "updateWaitTime": _0_service.AdminService._d_updateWaitTime, "updateRoundTime": _0_service.AdminService._d_updateRoundTime, "getWaitTime": _0_service.AdminService._d_getWaitTime, "getRoundTime": _0_service.AdminService._d_getRoundTime}

AdminService._omni_skeleton = AdminService
_0_service__POA.AdminService = AdminService
omniORB.registerSkeleton(AdminService._NP_RepositoryId, AdminService)
del AdminService
__name__ = "service"

# interface LeaderboardService
_0_service._d_LeaderboardService = (omniORB.tcInternal.tv_objref, "IDL:service/LeaderboardService:1.0", "LeaderboardService")
omniORB.typeMapping["IDL:service/LeaderboardService:1.0"] = _0_service._d_LeaderboardService
_0_service.LeaderboardService = omniORB.newEmptyClass()
class LeaderboardService :
    _NP_RepositoryId = _0_service._d_LeaderboardService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


    # typedef ... PlayerScores
    class PlayerScores:
        _NP_RepositoryId = "IDL:service/LeaderboardService/PlayerScores:1.0"
        def __init__(self, *args, **kw):
            raise RuntimeError("Cannot construct objects of this type.")
    _d_PlayerScores  = (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:service/PlayerAccount:1.0"], 0)
    _ad_PlayerScores = (omniORB.tcInternal.tv_alias, PlayerScores._NP_RepositoryId, "PlayerScores", (omniORB.tcInternal.tv_sequence, omniORB.typeMapping["IDL:service/PlayerAccount:1.0"], 0))
    _tc_PlayerScores = omniORB.tcInternal.createTypeCode(_ad_PlayerScores)
    omniORB.registerType(PlayerScores._NP_RepositoryId, _ad_PlayerScores, _tc_PlayerScores)


_0_service.LeaderboardService = LeaderboardService
_0_service._tc_LeaderboardService = omniORB.tcInternal.createTypeCode(_0_service._d_LeaderboardService)
omniORB.registerType(LeaderboardService._NP_RepositoryId, _0_service._d_LeaderboardService, _0_service._tc_LeaderboardService)

# LeaderboardService operations and attributes
LeaderboardService._d_getTopPlayers = ((), (omniORB.typeMapping["IDL:service/LeaderboardService/PlayerScores:1.0"], ), None)
LeaderboardService._d_incrementWins = (((omniORB.tcInternal.tv_string,0), ), (), None)

# LeaderboardService object reference
class _objref_LeaderboardService (CORBA.Object):
    _NP_RepositoryId = LeaderboardService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def getTopPlayers(self, *args):
        return self._obj.invoke("getTopPlayers", _0_service.LeaderboardService._d_getTopPlayers, args)

    def incrementWins(self, *args):
        return self._obj.invoke("incrementWins", _0_service.LeaderboardService._d_incrementWins, args)

omniORB.registerObjref(LeaderboardService._NP_RepositoryId, _objref_LeaderboardService)
_0_service._objref_LeaderboardService = _objref_LeaderboardService
del LeaderboardService, _objref_LeaderboardService

# LeaderboardService skeleton
__name__ = "service__POA"
class LeaderboardService (PortableServer.Servant):
    _NP_RepositoryId = _0_service.LeaderboardService._NP_RepositoryId


    _omni_op_d = {"getTopPlayers": _0_service.LeaderboardService._d_getTopPlayers, "incrementWins": _0_service.LeaderboardService._d_incrementWins}

LeaderboardService._omni_skeleton = LeaderboardService
_0_service__POA.LeaderboardService = LeaderboardService
omniORB.registerSkeleton(LeaderboardService._NP_RepositoryId, LeaderboardService)
del LeaderboardService
__name__ = "service"

# struct LoginResult
_0_service.LoginResult = omniORB.newEmptyClass()
class LoginResult (omniORB.StructBase):
    _NP_RepositoryId = "IDL:service/LoginResult:1.0"

    def __init__(self, success, wasForcedLogout, sessionId):
        self.success = success
        self.wasForcedLogout = wasForcedLogout
        self.sessionId = sessionId

_0_service.LoginResult = LoginResult
_0_service._d_LoginResult  = (omniORB.tcInternal.tv_struct, LoginResult, LoginResult._NP_RepositoryId, "LoginResult", "success", omniORB.tcInternal.tv_boolean, "wasForcedLogout", omniORB.tcInternal.tv_boolean, "sessionId", (omniORB.tcInternal.tv_string,0))
_0_service._tc_LoginResult = omniORB.tcInternal.createTypeCode(_0_service._d_LoginResult)
omniORB.registerType(LoginResult._NP_RepositoryId, _0_service._d_LoginResult, _0_service._tc_LoginResult)
del LoginResult

# interface LoginService
_0_service._d_LoginService = (omniORB.tcInternal.tv_objref, "IDL:service/LoginService:1.0", "LoginService")
omniORB.typeMapping["IDL:service/LoginService:1.0"] = _0_service._d_LoginService
_0_service.LoginService = omniORB.newEmptyClass()
class LoginService :
    _NP_RepositoryId = _0_service._d_LoginService[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_service.LoginService = LoginService
_0_service._tc_LoginService = omniORB.tcInternal.createTypeCode(_0_service._d_LoginService)
omniORB.registerType(LoginService._NP_RepositoryId, _0_service._d_LoginService, _0_service._tc_LoginService)

# LoginService operations and attributes
LoginService._d_loginPlayer = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.typeMapping["IDL:service/LoginResult:1.0"], ), {_0_service.InvalidCredentials._NP_RepositoryId: _0_service._d_InvalidCredentials, _0_service.AlreadyLoggedIn._NP_RepositoryId: _0_service._d_AlreadyLoggedIn})
LoginService._d_loginAdmin = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.typeMapping["IDL:service/LoginResult:1.0"], ), {_0_service.InvalidCredentials._NP_RepositoryId: _0_service._d_InvalidCredentials, _0_service.AlreadyLoggedIn._NP_RepositoryId: _0_service._d_AlreadyLoggedIn})
LoginService._d_forceLoginPlayer = (((omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0), (omniORB.tcInternal.tv_string,0)), (omniORB.typeMapping["IDL:service/LoginResult:1.0"], ), {_0_service.InvalidCredentials._NP_RepositoryId: _0_service._d_InvalidCredentials})
LoginService._d_logoutPlayer = (((omniORB.tcInternal.tv_string,0), ), (), None)

# LoginService object reference
class _objref_LoginService (CORBA.Object):
    _NP_RepositoryId = LoginService._NP_RepositoryId

    def __init__(self, obj):
        CORBA.Object.__init__(self, obj)

    def loginPlayer(self, *args):
        return self._obj.invoke("loginPlayer", _0_service.LoginService._d_loginPlayer, args)

    def loginAdmin(self, *args):
        return self._obj.invoke("loginAdmin", _0_service.LoginService._d_loginAdmin, args)

    def forceLoginPlayer(self, *args):
        return self._obj.invoke("forceLoginPlayer", _0_service.LoginService._d_forceLoginPlayer, args)

    def logoutPlayer(self, *args):
        return self._obj.invoke("logoutPlayer", _0_service.LoginService._d_logoutPlayer, args)

omniORB.registerObjref(LoginService._NP_RepositoryId, _objref_LoginService)
_0_service._objref_LoginService = _objref_LoginService
del LoginService, _objref_LoginService

# LoginService skeleton
__name__ = "service__POA"
class LoginService (PortableServer.Servant):
    _NP_RepositoryId = _0_service.LoginService._NP_RepositoryId


    _omni_op_d = {"loginPlayer": _0_service.LoginService._d_loginPlayer, "loginAdmin": _0_service.LoginService._d_loginAdmin, "forceLoginPlayer": _0_service.LoginService._d_forceLoginPlayer, "logoutPlayer": _0_service.LoginService._d_logoutPlayer}

LoginService._omni_skeleton = LoginService
_0_service__POA.LoginService = LoginService
omniORB.registerSkeleton(LoginService._NP_RepositoryId, LoginService)
del LoginService
__name__ = "service"

#
# End of module "service"
#
__name__ = "UserService_idl"

_exported_modules = ( "service", )

# The end.
