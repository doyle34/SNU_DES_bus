import simpy
from random import normalvariate, expovariate
import numpy as np

'''
word definition

passenger == psn: 승객
passenger inter-arrival time == psn_iat: 승객이 정류장의 승차 대기열에 도착하는 시간 간격
passenger inter-departure time == psn_idt: 승객이 정류장의 하차 대기열에 추가되는 시간 간격
bus inter-arrival time == bus_iat: 버스가 정류장 사이를 운행하는 시간 간격

(name)_dist: (name)의 distribution 정보를 담음. 보통 정규분포의 평균과 표준편차.
    ex) psn_iat_dist 는 psn_iat 의 분포 정보를 담고 있음. np.array([mean, std]) 형식.
(name)_list: (name)의 python list. numpy array 와 다름
    ex) psn_iat_dist_list 는 psn_iat_dist 의 list.
    psn_iat_dist 는 np.array([mean, std]) 형식 이므로
    psn_iat_dist_list 는 list(np.array([mean, std])) 형식임

bus_iat_dist_list[i]은 station[i - 1]에서 station[i] 까지 걸리는 시간에 대한 분포임
i = 0일때는 버스가 출발하고 0번째 station 에 도착하는 시간을 의미


simpy.Store() class
items: list of items
capacity: Maximum capacity
put(): request to put a/many item(s) in store
get(): request to get an item in store
put(), get()은 request 이므로 yield 할 시에 함수가 실행될 때 까지 진행되지 않음
store 의 capacity 가 무한하면 yield put() 을 해도 아무 문제 없음.
그러나 빈 store 에서 yield get() 을 할 경우 코드 진행이 멈춤에 주의
get(), put() 또한 request 의 일종이니 with ~ as ~: 구문을 사용해야 함 (확실하지않음)

'''


class Bus:
    def __init__(self, env, bus_cap, stations, iat_dist_list):
        self.env = env
        self.station_idx = 0
        self.stations = stations
        self.passengers = simpy.Store(self.env, capacity=bus_cap)
        self.iat_dist = iat_dist_list
        self.driving_process = self.env.process(self.drive())

    def arrive(self, station):
        # bus arrives at a station, and passengers get off
        temp_cnt = 0
        for i in range(station.n_psn_depart):
            if self.passengers.items:
                with self.passengers.get() as psn_get:
                    yield psn_get
                    temp_cnt += 1

        print(f'{temp_cnt} passengers get off at {station.name}: {self.env.now}')
        station.n_psn_depart = 0
        temp_cnt = 0
        # after passengers get off, new passengers board
        # print(f'passengers starts boarding at {station.name}: {self.env.now}')
        while station.boarding_queue.items:
            with station.boarding_queue.get() as st_get:
                passenger_now = yield st_get
                with self.passengers.put(passenger_now) as psn_put:
                    yield psn_put
                    temp_cnt += 1

        print(f'{temp_cnt} passengers board at {station.name}: {self.env.now}')

    def drive(self):
        while True:
            for station, iat in zip(self.stations, self.iat_dist):
                yield self.env.timeout(normalvariate(iat[0], iat[1]))  # bus moves to next station
                print(f'bus arrives at station {self.station_idx}: {self.env.now}')
                yield self.env.process(self.arrive(station))  # bus arrives at station[i]
                self.station_idx += 1
            # bus finishes driving for one cycle
            print('bus finishes driving for one cycle')
            yield self.env.timeout(5)  # wait 5 minute for next driving cycle
            print('bus returns to first station')
            self.station_idx = 0


class Station:
    def __init__(self, env, name, psn_iat_dist, psn_idt_dist):
        self.env = env
        self.name = name
        self.n_psn_depart = 0
        self.boarding_queue = simpy.Store(self.env)
        self.psn_iat_dist = psn_iat_dist
        self.psn_idt_dist = psn_idt_dist
        self.arrival_process = self.env.process(self.passenger_arrive())
        self.departure_process = self.env.process(self.passenger_depart())

    def passenger_arrive(self):
        psn_cnt = 0
        while True:
            yield self.env.timeout(normalvariate(self.psn_iat_dist[0], self.psn_iat_dist[1]))
            # new passenger arrives at this station
            passenger = Passenger('Passenger %i' % psn_cnt)
            yield self.boarding_queue.put(passenger)
            # print(f"{len(self.boarding_queue.items)} passengers waiting at {self.name}: {round(self.env.now, 2)}")
            psn_cnt += 1

    def passenger_depart(self):
        while True:
            yield self.env.timeout(normalvariate(self.psn_idt_dist[0], self.psn_idt_dist[1]))
            # new passenger wants to get off at this station
            self.n_psn_depart += 1
            # print(f"{self.n_psn_depart} passengers will leave at {self.name}: {round(self.env.now, 2)}")


class Passenger:
    def __init__(self, name):
        self.name = name


n_stations = 9
bus_capacity = 50
SIM_TIME = 60
# list of passenger arrival time distribution (mean, std) for each stations.
psn_iat_dist_list = [np.array([1, 0]) for i in range(n_stations)]
# list of passenger departure time distribution (mean, std) for each stations
psn_idt_dist_list = [np.array([1, 0]) for i in range(n_stations)]
# bus IAT distribution (mean, std) between stations
bus_iat_dist_list = [np.array([5, 0]) for i in range(n_stations)]

env = simpy.Environment()
stations = [Station(env, 'Station %i' % i, piat, pidt)
            for i, (piat, pidt) in enumerate(zip(psn_iat_dist_list, psn_idt_dist_list))]
bus = Bus(env, bus_capacity, stations, bus_iat_dist_list)

env.run(until=SIM_TIME)
print('simulation end')
