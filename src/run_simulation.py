import simpy
from bus_system import Bus, Station, Passenger, generate_buses
from random import normalvariate, expovariate
import numpy as np
import pandas as pd

# system configuration
n_stations = 9
n_bus = 6
bus_capacity = 50
SIM_TIME = 180

#
total_passengers = 0 ############################
total_driving_time = 0 ##########################

# list of passenger arrival time distribution (mean, std) for each stations.
psn_iat_df = pd.read_csv("Passenger_DATA_v2/psn_iat.csv")
psn_iat_dist_list = [np.array([psn_iat_df["average"][i], 0]) for i in range(n_stations)]
# list of passenger departure time distribution (mean, std) for each stations
psn_idt_df = pd.read_csv("Passenger_DATA_v2/psn_idt.csv")
psn_idt_dist_list = [np.array([psn_idt_df["average"][i], 0]) for i in range(n_stations)]
# bus IAT distribution (mean, std) between stations
bus_iat_df = pd.read_csv("bus_data_v2/bus_iat.csv")
bus_iat_dist_list = [np.array([bus_iat_df["average"][i], bus_iat_df["std"][i]]) for i in range(n_stations)]
# bus inter-dispatch time distribution (mean, std)
bus_idt_df = pd.read_csv("bus_data_v2/bus_idt.csv")
bus_idt_dist_list = [np.array([bus_idt_df["mean"][i], bus_idt_df["std"][i]]) for i in range(18)]

# average value of one day
# bus_idt_dist = np.array([10, 0])
bus_idt_dist = np.array([bus_idt_df["mean"][18], bus_idt_df["std"][18]])


env = simpy.Environment()
stations = [Station(env, f'S{i}', piat, pidt)
            for i, (piat, pidt) in enumerate(zip(psn_iat_dist_list, psn_idt_dist_list))]
stations[-1].is_terminal = True
buses = []
env.process(generate_buses(env, bus_capacity, stations, bus_iat_dist_list, bus_idt_dist, n_bus, buses))
env.run(until=SIM_TIME)

print('simulation end')
for bus in buses:
    print(f'{bus.name} transported {bus.psn_cnt} passengers during {bus.driving_time} min') ##############
    total_passengers += bus.psn_cnt ######################################
    total_driving_time += bus.driving_time ###############################

print(f'total passengers: {total_passengers}')############################
print(f'total driving time: {total_driving_time}')############################