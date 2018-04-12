from abc import ABCMeta, abstractmethod


class Module(metaclass=ABCMeta):

    @abstractmethod
    def receive_message(self):
        pass

    @abstractmethod
    def send_message(self, message):
        pass


class Core(Module):

    def receive_message(self):
        print("message recieved")

    def send_message(self, message):
        print("message '{}' sent".format(message))


class WeatherModule(Module):

    def __init__(self, decorated):
        self.decorated = decorated

    def receive_message(self):
        self.decorated.receive_message()

    def send_message(self, message):
        self.decorated.send_message(message)

    def get_weather(self):
        return 'WEATHER: today is sunny'


class RoadModule(Module): # if it inherits by WeatherModule all works

    def __init__(self, decorated):
        self.decorated = decorated

    def receive_message(self):
        self.decorated.receive_message()

    def send_message(self, message):
        self.decorated.send_message(message)

    def get_crowd(self):
        return 'ROAD: roads are crowded today'


if __name__ == '__main__':

    #today = RoadModule(WeatherModule(Core()))
    today = WeatherModule(RoadModule(Core())) # it is wrong way. how it works in Java?
    print(today.get_crowd())
    print(today.get_weather())
