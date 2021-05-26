import simpy
from random import normalvariate, expovariate


class Bus:
    def __init__(self, env, name, bus_cap, stations, iat_dist_list):
        self.env = env
        self.name = name
        self.station_idx = 0
        self.stations = stations
        self.passengers = simpy.Store(self.env, capacity=bus_cap)
        self.psn_cnt = 0
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

        print(f'{temp_cnt} passengers get off from {self.name} at {station.name}: {self.env.now}')
        station.n_psn_depart = 0
        temp_cnt = 0
        # after passengers get off, new passengers board
        while station.boarding_queue.items:
            if len(self.passengers.items) == self.passengers.capacity:  # if bus is full
                print(f'{self.name} is full, so passengers in {station.name} renege')
                current_len = len(station.boarding_queue.items)
                while len(station.boarding_queue.items) < current_len / 2:
                    yield station.boarding_queue.get()  # half of passengers in boarding queue leaves
                break  # forced while loop exit

            else:  # if bus is not full
                passenger_now = yield station.boarding_queue.get()
                yield self.passengers.put(passenger_now)
                temp_cnt += 1
                self.psn_cnt += 1

        print(f'{temp_cnt} passengers board to {self.name} at {station.name}: {self.env.now}')

    def drive(self):
        while True:
            for station, iat in zip(self.stations, self.iat_dist):
                yield self.env.timeout(normalvariate(iat[0], iat[1]))  # bus moves to next station
                print(f'{self.name} arrives at {station.name}: {self.env.now}')
                yield self.env.process(self.arrive(station))  # bus arrives at station[i]
                self.station_idx += 1
            # bus finishes driving for one cycle
            print(f'{self.name} finishes driving for one cycle')
            yield self.env.timeout(5)  # wait 5 minute for next driving cycle
            print(f'{self.name} returns to first station')
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
        cnt = 0
        while True:
            yield self.env.timeout(normalvariate(self.psn_iat_dist[0], self.psn_iat_dist[1]))
            # new passenger arrives at this station
            psn_code = 'P' + str(cnt).zfill(3)
            passenger = Passenger(self.name + psn_code)
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


def generate_buses(env, bus_capacity, stations, bus_iat_dist_list, idt_dist, n_bus, buses):
    for i in range(n_bus):
        yield env.timeout(normalvariate(idt_dist[0], idt_dist[1]))
        buses.append(Bus(env, f'B{i}', bus_capacity, stations, bus_iat_dist_list))
