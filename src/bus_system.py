import simpy
import math
import numpy as np
from random import normalvariate, expovariate


class Bus:
    def __init__(self, env, name, bus_cap, stations):
        self.env = env
        self.name = name
        self.station_idx = 0
        self.stations = stations
        self.bus_idt_dist = np.array([13.5, 2.475])
        self.passengers = simpy.Store(self.env, capacity=bus_cap)
        self.psn_cnt = 0
        self.driving_process = self.env.process(self.drive())
        self.driving_time = 0

    def arrive(self, station):
        # bus arrives at a station, and passengers get off
        temp_cnt = 0
        if station.is_terminal:  # if bus arrived at terminal
            while self.passengers.items:
                yield self.passengers.get()
        else:
            for i in range(station.n_psn_depart):
                if self.passengers.items:
                    yield self.passengers.get()
                    temp_cnt += 1

        print(f'{temp_cnt} passengers get off from {self.name} at {station.name}: {self.env.now}')
        station.n_psn_depart = 0
        temp_cnt = 0
        # after passengers get off, new passengers board
        while station.boarding_queue.items:
            if len(self.passengers.items) == self.passengers.capacity:  # if bus is full
                print(f'{self.name} is full, so passengers in {station.name} renege')
                current_len = len(station.boarding_queue.items)
                while len(station.boarding_queue.items) < current_len / 2:
                    passenger_renege = yield station.boarding_queue.get()  # half of passengers in boarding queue leaves
                    passenger_renege.renege(self.env)
                    station.psn_waiting_time.append(passenger_renege.waiting_time)
                    station.n_psn_renege += 1

                break  # forced while loop exit

            else:  # if bus is not full
                passenger_now = yield station.boarding_queue.get()
                passenger_now.board(self.env)
                station.psn_waiting_time.append(passenger_now.waiting_time)
                yield self.passengers.put(passenger_now)
                temp_cnt += 1
                self.psn_cnt += 1

        print(f'{temp_cnt} passengers board to {self.name} at {station.name}: {self.env.now}')

    def drive(self):
        while True:
            for station in self.stations:
                driving_time_single = normalvariate(station.bus_iat_dist[0], station.bus_iat_dist[1])
                yield self.env.timeout(driving_time_single)  # bus moves to next station
                self.driving_time += driving_time_single
                print(f'{self.name} arrives at {station.name}: {self.env.now}')
                yield self.env.process(self.arrive(station))  # bus arrives at station[i]
                self.station_idx += 1
            # bus finishes driving for one cycle
            print(f'{self.name} finishes driving for one cycle')
            dispatch_time = normalvariate(self.bus_idt_dist[0], self.bus_idt_dist[1])
            yield self.env.timeout(dispatch_time)
            print(f'{self.name} returns to first station')
            self.station_idx = 0


class Station:
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.is_terminal = False
        self.n_psn_depart = 0
        self.n_psn_renege = 0
        self.boarding_queue = simpy.Store(self.env)
        self.psn_waiting_time = []
        self.psn_iat_dist = np.array([10, 0.01])
        self.psn_idt_dist = np.array([10, 0.01])
        self.bus_iat_dist = np.array([7, 0.1])
        self.arrival_process = self.env.process(self.passenger_arrive())
        self.departure_process = self.env.process(self.passenger_depart())

    def passenger_arrive(self):
        cnt = 0
        while True:
            yield self.env.timeout(normalvariate(self.psn_iat_dist[0], self.psn_iat_dist[1]))
            # new passenger arrives at this station
            psn_code = 'P' + str(cnt).zfill(3)
            passenger = Passenger(self.name + psn_code)
            passenger.start_waiting(self.env)
            yield self.boarding_queue.put(passenger)
            cnt += 1

    def passenger_depart(self):
        while True:
            yield self.env.timeout(normalvariate(self.psn_idt_dist[0], self.psn_idt_dist[1]))
            # new passenger wants to get off at this station
            self.n_psn_depart += 1


class Passenger:
    def __init__(self, name):
        self.name = name
        self.waiting_start = 0
        self.waiting_end = 0
        self.waiting_time = 0
        self.reneged = False

    def start_waiting(self, env):
        self.waiting_start = env.now

    def board(self, env):
        self.waiting_end = env.now
        self.waiting_time = self.waiting_end - self.waiting_start

    def renege(self, env):
        self.waiting_end = env.now
        self.waiting_time = self.waiting_end - self.waiting_start
        self.reneged = True


def generate_buses(env, bus_capacity, stations, bus_idt_df, n_bus, buses):
    for i in range(n_bus):
        j = math.floor(env.now / 60)
        new_bus = Bus(env, f'B{i}', bus_capacity, stations)
        new_bus.bus_idt_dist = np.array([bus_idt_df.iloc[j, 1], bus_idt_df.iloc[j, 2]])
        buses.append(new_bus)
        yield env.timeout(normalvariate(bus_idt_df.iloc[j, 1], bus_idt_df.iloc[j, 2]))


def dist_change(env, stations, buses, df_list, temp_cnt):
    time_zone = 18
    psn_iat_df, psn_idt_df, bus_iat_df, bus_idt_df = df_list
    while True:
        for j in range(time_zone):
            for i, station in enumerate(stations):
                station.psn_iat_dist = np.array([psn_iat_df.iloc[i, j + 1], 0.01])
                station.psn_idt_dist = np.array([psn_idt_df.iloc[i, j + 1], 0.01])
                station.bus_iat_dist = np.array([bus_iat_df.iloc[i, j + 1], 0.1])

            for bus in buses:
                bus.bus_idt_dist = np.array([bus_idt_df.iloc[j, 1], bus_idt_df.iloc[j, 2]])

            temp_cnt.append(0)
            yield env.timeout(60)


def monitor(env, stations, waiting_times):
    while True:
        yield env.timeout(60)
        waiting_times_col = []
        for station in stations:
            if len(station.psn_waiting_time) > 0:
                average_waiting_time = sum(station.psn_waiting_time) / len(station.psn_waiting_time)
            else:
                average_waiting_time = 0

            waiting_times_col.append(average_waiting_time)

        waiting_times.append(waiting_times_col)
