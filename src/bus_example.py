import simpy
import random
import numpy as np


class Bus:
    def __init__(self, env):
        self.env = env
        self.station_idx = 0
        self.capacity = 50
        self.available_seat = 50
        self.passengers = simpy.Store(self.env, capacity=self.capacity)

    def arrival(self, station):
        # bus arrives at a station, and passengers get off
        for i in range(station.getoffpeople):
            yield self.passengers.get()

        # after passengers get off, new passengers board
        while len(station.items) > 0:
            passenger_now = yield station.get()
            yield self.passengers.put(passenger_now)

    def drive(self):
        yield self.env.timeout(10)
        self.station_idx += 1


class Station(simpy.Store):
    def __init__(self, env):
        super().__init__(env)
        self.env = env
        self.getoffpeople = 5
        self.boardpeople = 5

    def passenger_arrival(self, passenger):
        yield self.put(passenger)

    def bus_arrival(self, bus):
        while len(self.items) > 0:
            passenger_now = yield self.get()
            yield bus.passengers.put(passenger_now)


class Passenger:
    def __init__(self, name):
        self.name = name


# def generate_passenger(station):