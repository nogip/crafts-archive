# here realised two patterns: Facade and Bridge

from abc import ABCMeta, abstractmethod

class IBotFacade(metaclass=ABCMeta):

    @abstractmethod
    def reply(self, message):
        pass

    @abstractmethod
    def broadcast(self, message):
        pass

#################################################################
class IReplyBridge(metaclass=ABCMeta):

    @abstractmethod
    def reply(self, message):
        pass

class ReplyBridge(IReplyBridge):

    def __init__(self, implementation):
        self._implementation = implementation

    def reply(self, message):
        self._implementation.reply(message)

class IReplyImplement(metaclass=ABCMeta):

    @abstractmethod
    def reply(self, message):
        pass

class BadReplyImplement(IReplyImplement):

    def reply(self, message):
        print("BAD_REPLY: {}".format(message))

class CoolReplyImplement(IReplyImplement):

    def reply(self, message):
        print("COOL_REPLY: {}".format(message))
###############################################################

class IBroadcastBridge(metaclass=ABCMeta):

    @abstractmethod
    def broadcast(self, message):
        pass

class BroadcastBridge(IBroadcastBridge):

    def __init__(self, implementation):
        self._implementation = implementation

    def broadcast(self, message):
        self._implementation.broadcast(message)

class IBroadcastImplement(metaclass=ABCMeta):

    @abstractmethod
    def broadcast(self, message):
        pass

class AdminBroadcast(IBroadcastImplement):

    def broadcast(self, message):
        print("ADMIN_BROADCAST: {}". format(message))

class MembersBroadcast(IBroadcastImplement):

    def broadcast(self, message):
        print("MEMBER_BROADCAST: {}".format(message))

class BotFacade(IBotFacade):

    def __init__(self):
        self._reply = ReplyBridge(CoolReplyImplement())
        self._broadcast = BroadcastBridge(MembersBroadcast())

    def reply(self, message):
        self._reply.reply(message)

    def broadcast(self, message):
        self._broadcast.broadcast(message)


if __name__ == '__main__':
    bot = BotFacade()
    bot.broadcast('Anybody there?')
    bot.reply("No one, dude.")
