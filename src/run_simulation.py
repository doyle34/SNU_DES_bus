import simpy
from bus_system import Bus, Station, Passenger, generate_buses
from random import normalvariate, expovariate
import numpy as np

# system configuration
n_stations = 9
n_bus = 4
bus_capacity = 50
SIM_TIME = 180
# list of passenger arrival time distribution (mean, std) for each stations.
psn_iat_dist_list = [np.array([1, 0]) for i in range(n_stations)]
# list of passenger departure time distribution (mean, std) for each stations
psn_idt_dist_list = [np.array([1, 0]) for i in range(n_stations)]
# bus IAT distribution (mean, std) between stations
bus_iat_dist_list = [np.array([5, 0]) for i in range(n_stations)]
# bus inter-dispatch time distribution (mean, std)
bus_idt_dist = np.array([10, 0])

env = simpy.Environment()
stations = [Station(env, f'S{i}', piat, pidt)
            for i, (piat, pidt) in enumerate(zip(psn_iat_dist_list, psn_idt_dist_list))]
buses = []
env.process(generate_buses(env, bus_capacity, stations, bus_iat_dist_list, bus_idt_dist, n_bus, buses))
env.run(until=SIM_TIME)
print('simulation end')
for bus in buses:
    print(f'{bus.name} transported {bus.psn_cnt} passengers during {SIM_TIME} min')
