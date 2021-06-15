import simpy
import math
import numpy as np
from random import normalvariate


class Bus:
    def __init__(self, env, bus_info, stations):
        self.env = env
        self.name = bus_info["name"]
        self.category = bus_info["category"]
        self.fuel = bus_info["fuel"]
        self.model = bus_info["model"]
        self.cost = 0
        self.stations = stations
        self.bus_idt_dist = np.array([13.5, 2.475])
        self.passengers = simpy.Store(self.env, capacity=bus_info["capacity"])
        self.psn_cnt = 0
        self.driving_time = 0
        self.driving_distance = 0
        self.driving_process = 0

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

        station.n_hr_psn_depart += temp_cnt
        station.n_psn_depart = 0
        temp_cnt = 0
        # after passengers get off, new passengers board
        while station.boarding_queue.items:
            if len(self.passengers.items) == self.passengers.capacity:  # if bus is full
                current_len = len(station.boarding_queue.items)
                while len(station.boarding_queue.items) > current_len / 2:
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

        station.n_hr_psn_board += temp_cnt

    def drive(self):
        while True:
            for station in self.stations:
                driving_time_single = normalvariate(station.bus_iat_dist[0], station.bus_iat_dist[1])
                yield self.env.timeout(driving_time_single)  # bus moves to next station
                self.driving_time += driving_time_single
                self.driving_distance += station.distance
                yield self.env.process(self.arrive(station))  # bus arrives at station[i]
            # bus finishes driving for one cycle
            dispatch_time = max(normalvariate(self.bus_idt_dist[0], self.bus_idt_dist[1]), 10)
            real_dispatch_time = max(dispatch_time - normalvariate(self.stations[0].bus_iat_dist[0],
                                                     self.stations[0].bus_iat_dist[1]), 0)
            yield self.env.timeout(real_dispatch_time)

    def calculate_cost(self, bus_cost):
        fuel_cost = bus_cost[self.fuel]
        operation_cost = bus_cost['operational']
        retain_cost = bus_cost['retain']
        self.cost = int(fuel_cost * self.driving_distance + operation_cost + retain_cost)
        # print(f'total bus cost: {total_bus_cost}')

    def dispatch(self):
        self.driving_process = self.env.process(self.drive())


class Station:
    def __init__(self, env, name, distance):
        self.env = env
        self.name = name
        self.distance = distance  # distance to current station
        self.is_terminal = False
        self.boarding_queue = simpy.Store(self.env)
        self.psn_iat_dist = np.array([10, 0.01])
        self.psn_idt_dist = np.array([10, 0.01])
        self.bus_iat_dist = np.array([7, 0.1])
        self.n_psn_depart = 0
        self.n_psn_renege = 0
        self.n_hr_psn_board = 0
        self.n_hr_psn_depart = 0
        self.psn_waiting_time = []
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


def dispatch_buses(env, bus_idt_df, buses):
    for bus in buses:
        j = math.floor(env.now / 60)
        bus.dispatch()
        yield env.timeout(normalvariate(bus_idt_df.iloc[j,0], bus_idt_df.iloc[j,1]))


def dist_change(env, stations, buses, df_list):
    time_zone = 18
    psn_iat_df, psn_idt_df, bus_iat_df, bus_idt_df = df_list
    while True:
        for j in range(time_zone):
            for i, station in enumerate(stations):
                station.psn_iat_dist = np.array([psn_iat_df.iloc[i, j + 1], 0.01])
                station.psn_idt_dist = np.array([psn_idt_df.iloc[i, j + 1], 0.01])
                station.bus_iat_dist = np.array([bus_iat_df.iloc[i, j + 1], 0.1])

            for bus in buses:
                bus.bus_idt_dist = np.array([bus_idt_df.iloc[j,0], bus_idt_df.iloc[j,1]])

            yield env.timeout(60)


def monitor(env, stations, buses, hour_summaries):
    prev_board = np.zeros(20)
    prev_depart = np.zeros(20)
    prev_renege = np.zeros(20)
    prev_cnt = np.zeros(20)
    prev_time = np.zeros(20)
    prev_distance = np.zeros(20)
    while True:
        yield env.timeout(60)
        psn_board_col = []
        psn_depart_col = []
        psn_renege_col = []
        psn_cnt_col = []
        driving_time_col = []
        driving_distance_col = []
        waiting_times_col = []
        for i, station in enumerate(stations):
            if len(station.psn_waiting_time) > 0:
                average_waiting_time = sum(station.psn_waiting_time) / len(station.psn_waiting_time)
            else:
                average_waiting_time = 0

            psn_board = station.n_hr_psn_board - prev_board[i]
            psn_depart = station.n_hr_psn_depart - prev_depart[i]
            psn_renege = station.n_psn_renege - prev_renege[i]

            psn_board_col.append(psn_board)
            psn_depart_col.append(psn_depart)
            psn_renege_col.append(psn_renege)
            waiting_times_col.append(average_waiting_time)

            prev_board[i] += psn_board
            prev_depart[i] += psn_depart
            prev_renege[i] += psn_renege

        for i, bus in enumerate(buses):
            psn_cnt = bus.psn_cnt - prev_cnt[i]
            driving_time = bus.driving_time - prev_time[i]
            driving_distance = bus.driving_distance - prev_distance[i]

            psn_cnt_col.append(psn_cnt)
            driving_time_col.append(driving_time)
            driving_distance_col.append(driving_distance)

            prev_cnt[i] += psn_cnt
            prev_time[i] += driving_time
            prev_distance[i] += driving_distance

        hour_summaries[0].append(psn_board_col)
        hour_summaries[1].append(psn_depart_col)
        hour_summaries[2].append(psn_renege_col)
        hour_summaries[3].append(waiting_times_col)
        hour_summaries[4].append(psn_cnt_col)
        hour_summaries[5].append(driving_time_col)
        hour_summaries[6].append(driving_distance_col)
