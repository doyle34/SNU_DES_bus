import simpy
from bus_system import *
from random import normalvariate, expovariate
import numpy as np
import pandas as pd
import csv

# system configuration
n_stations = 9
# n_bus = 6
time_zone = 18
# bus_capacity = 53
SIM_TIME = 60 * time_zone + 1

#
total_passengers = 0
total_driving_time = 0
total_driving_distance = 0

# list of passenger arrival time distribution (mean, std) for each stations.
psn_iat_df = pd.read_csv("passenger_data/psn_iat.csv")
# list of passenger departure time distribution (mean, std) for each stations
psn_idt_df = pd.read_csv("passenger_data/psn_idt.csv")
# bus IAT distribution (mean, std) between stations
bus_iat_df = pd.read_csv("bus_data/bus_iat.csv")
# bus inter-dispatch time distribution (mean, std)
bus_idt_df = pd.read_csv("bus_data/bus_idt.csv")

# bus information (bus_name, category, bus_model, bus_capacity)
bus_info_df = pd.read_csv("bus_data/bus_info.csv")

df_list = [psn_iat_df, psn_idt_df, bus_iat_df, bus_idt_df]

env = simpy.Environment()
stations = [Station(env, f'S{i}', distance) for i, distance in enumerate(bus_iat_df['distance'])]
stations[-1].is_terminal = True
buses = []
env.process(generate_buses(env, bus_info_df, stations, bus_idt_df, buses))
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
    total_driving_distance += bus.driving_distance


for station in stations:
    if len(station.psn_waiting_time) > 0:
        average_waiting_time = sum(station.psn_waiting_time) / len(station.psn_waiting_time)
    else:
        average_waiting_time = 0

    print(f'average passenger waiting time at {station.name}: {round(average_waiting_time, 2)}')
    print(f'{station.n_psn_renege} passengers reneged at {station.name}')

print(f'total passengers: {total_passengers}')
print(f'total driving time: {total_driving_time}')
print(f'total driving distance: {total_driving_distance} ')
df_columns = psn_idt_df.columns.drop(['station', 'average', 'std'])
waiting_times_df = pd.DataFrame(np.transpose(np.array(waiting_times)), columns=df_columns)
waiting_times_df.to_csv('output/waiting_times.csv', sep=',')

# calculate total fee
age_fee_df = pd.read_csv('passenger_data/age_ratio_and_fee.csv')
total_fee = 0
for key, value in age_fee_df.iteritems():
    total_fee += total_passengers * value[0] * value[1]

print(f'total fee: {round(total_fee)}')

# calculate bus operating cost
large_bus_cost_df = pd.read_csv('bus_data/costs_large.csv')
small_bus_cost_df = pd.read_csv('bus_data/costs_small.csv')
total_bus_cost = 0

for bus in buses:
    if (bus.category == 'medium'):
        bus.calculate_cost(small_bus_cost_df)
    else:
        bus.calculate_cost(large_bus_cost_df)

    print(f'{bus.name} operaing cost : {bus.cost} won per day')
    total_bus_cost += bus.cost

print(f'total bus cost: {total_bus_cost}')

total_profit = total_fee - total_bus_cost
print(f'total profit: {total_profit}')