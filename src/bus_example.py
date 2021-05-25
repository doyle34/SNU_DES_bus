import simpy
from random import normalvariate, expovariate
import numpy as np

'''
word definition

passenger == psn: 승객
passenger arrival time == psn_arrival_time == psn_arr_t: 승객이 정류장의 승차 대기열에 도착하는 시간 간격
passenger getoff time == psn_getoff_time == psn_off_t: 승객이 정류장의 하차 대기열에 추가되는 시간 간격
bus_IAT: 버스가 정류장 사이를 운행하는 시간 간격
(name)_dist: (name)의 distribution 정보를 담음. 보통 정규분포의 평균과 표준편차.
    ex) psn_arr_t_dist 는 psn_arr_t 의 분포 정보를 담고 있음. np.array([mean, std]) 형식.
(name)_list: (name)의 python list. numpy array 와 다름
    ex) psn_arrival_time_dist_list 는 psn_arrival_time_dist 의 list.
    psn_arrival_time_dist 는 np.array([mean, std]) 형식 이므로
    psn_arrival_time_dist_list 는 list(np.array([mean, std])) 형식임

복잡한 변수명은 차차 정리할 예정
'''


class Bus:
    def __init__(self, env, stations, IAT_dist):
        self.env = env
        self.station_idx = 0
        self.stations = stations
        self.capacity = 50
        self.available_seat = 50
        self.passengers = simpy.Store(self.env, capacity=self.capacity)
        self.IAT_dist = IAT_dist
        self.driving_process = self.env.process(self.drive())

    def arrival(self, station):
        # bus arrives at a station, and passengers get off
        while station.n_psn_getoff > 0:
            yield self.passengers.get()

        # after passengers get off, new passengers board
        while len(station.boarding_queue) > 0:
            passenger_now = yield station.get()
            yield self.passengers.put(passenger_now)

    def drive(self):
        while True:
            yield self.env.timeout(normalvariate(self.IAT_dist[0], self.IAT_dist[1]))  # bus moves to next station
            yield self.arrival(self.stations[self.station_idx])  # bus arrives at station[i]
            self.station_idx += 1


class Station:
    def __init__(self, env, psn_arr_t_dist, psn_off_t_dist):
        self.env = env
        self.n_psn_getoff = 0
        self.boarding_queue = simpy.Store(self.env)
        self.psn_arr_t_dist = psn_arr_t_dist
        self.psn_off_t_dist = psn_off_t_dist
        self.arrival_process = self.env.process(self.passenger_arrival())
        self.getoff_process = self.env.process(self.passenger_getoff())

    def passenger_arrival(self):
        psn_cnt = 0
        while True:
            yield self.env.timeout(normalvariate(self.psn_arr_t_dist[0], self.psn_arr_t_dist[1]))
            # new passenger arrives at this station
            passenger = Passenger('Passenger %i' % psn_cnt)
            yield self.boarding_queue.put(passenger)
            psn_cnt += 1

    def passenger_getoff(self):
        while True:
            yield self.env.timeout(normalvariate(self.psn_off_t_dist[0], self.psn_off_t_dist[1]))
            # new passenger wants to get off at this station
            self.n_psn_getoff += 1


class Passenger:
    def __init__(self, name):
        self.name = name


n_stations = 9
# list of passenger arrival time distribution (mean, std) for each stations.
psn_arrival_time_dist_list = [np.array([1, 0]) for i in range(n_stations)]
# list of passenger getoff time distribution (mean, std) for each stations
psn_getoff_time_dist_list = [np.array([1, 0]) for i in range(n_stations)]
# bus IAT distribution (mean, std) between stations
bus_IAT_dist = [np.array([5, 0]) for i in range(n_stations)]

env = simpy.Environment()
stations = [Station(env, patd, pgtd) for patd, pgtd in zip(psn_arrival_time_dist_list, psn_getoff_time_dist_list)]

bus = Bus(env, stations, bus_IAT_dist)