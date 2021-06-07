import simpy
from bus_system import *
from random import normalvariate, expovariate
import numpy as np
import pandas as pd
import csv

# system configuration
n_stations = 9
n_bus = 6
time_zone = 18
bus_capacity = 50
SIM_TIME = 60 * time_zone + 1

#
total_passengers = 0
total_driving_time = 0

# list of passenger arrival time distribution (mean, std) for each stations.
psn_iat_df = pd.read_csv("passenger_data/psn_iat.csv")
# list of passenger departure time distribution (mean, std) for each stations
psn_idt_df = pd.read_csv("passenger_data/psn_idt.csv")
# bus IAT distribution (mean, std) between stations
bus_iat_df = pd.read_csv("bus_data/bus_iat.csv")
# bus inter-dispatch time distribution (mean, std)
bus_idt_df = pd.read_csv("bus_data/bus_idt.csv")

df_list = [psn_iat_df, psn_idt_df, bus_iat_df, bus_idt_df]

env = simpy.Environment()
stations = [Station(env, f'S{i}')
            for i in range(n_stations)]
stations[-1].is_terminal = True
buses = []
env.process(generate_buses(env, bus_capacity, stations, bus_idt_df, n_bus, buses))
temp_cnt = []
env.process(dist_change(env, stations, buses, df_list, temp_cnt))
waiting_times = []
env.process(monitor(env, stations, waiting_times))
env.run(until=SIM_TIME)

print(f'simulation end')
print(f'dist_change count = {len(temp_cnt)}')

for bus in buses:
    print(f'{bus.name} transported {bus.psn_cnt} passengers during {bus.driving_time} min')
    total_passengers += bus.psn_cnt
    total_driving_time += bus.driving_time


for station in stations:
    if len(station.psn_waiting_time) > 0:
        average_waiting_time = sum(station.psn_waiting_time) / len(station.psn_waiting_time)
    else:
        average_waiting_time = 0

    print(f'average passenger waiting time at {station.name}: {round(average_waiting_time, 2)}')
    print(f'{station.n_psn_renege} passengers reneged at {station.name}')

print(f'total passengers: {total_passengers}')
print(f'total driving time: {total_driving_time}')
df_columns = psn_idt_df.columns.drop(['station', 'average', 'std'])
waiting_times_df = pd.DataFrame(np.transpose(np.array(waiting_times)), columns=df_columns)
waiting_times_df.to_csv('output/waiting_times.csv', sep=',')
