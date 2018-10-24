from abc import ABCMeta, abstractmethod

class ITimetable(metaclass=ABCMeta):

    @abstractmethod
    def timetable(self):
        pass


class ITimetableImplement(metaclass=ABCMeta):

    @abstractmethod
    def generate_tt(self):
        pass

    def return_tt(self):
        pass


class SimpleTimetable(ITimetableImplement):

    def generate_tt(self):
        print('SIMPLE timetable generated')

    def return_tt(self):
        return 'Simple timetable'

class SophisticatedTimetable(ITimetableImplement):

    def generate_tt(self):
        print('SOPHISTICATED timetable generated')

    def return_tt(self):
        return 'Sophisticated timetable'


class Timetable(ITimetable):

    def __init__(self, tt):
        self.tt = tt

    def timetable(self):
        self.tt.generate_tt()
        return self.tt.return_tt()

if __name__ == '__main__':
    tt = Timetable(SimpleTimetable())
    print(tt.timetable())
    print("*" * 80)

    tt = Timetable(SophisticatedTimetable())
    print(tt.timetable())
