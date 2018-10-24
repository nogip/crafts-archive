from abc import ABCMeta, abstractmethod


class A(metaclass=ABCMeta):

    __instance__ = None

    @staticmethod
    def get_command_observer():
        if A.__instance__ is None:
            A.__instance__ = A()
        return A.__instance__

    def __init__(self):
        self.trigger = 'Base'

    def get_trigger(self):
        return self.trigger

    def set_trigger(self, trigger):
        self.trigger = trigger

class B(A):
    pass

class C(A):
    pass

if __name__ == '__main__':
    b = B.get_command_observer()
    b.set_trigger('b trig')
    print(b.get_trigger())

    c = C.get_command_observer()
    c.set_trigger('s trig')
    print(b.get_trigger())




