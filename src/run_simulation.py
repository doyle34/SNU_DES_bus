from bus_system import *
import numpy as np
import pandas as pd

# system setup
n_stations = 9
time_zone = 18
SIM_TIME = 60 * time_zone + 1

psn_iat_df = pd.read_csv("passenger_data/psn_iat.csv")
psn_idt_df = pd.read_csv("passenger_data/psn_idt.csv")
bus_iat_df = pd.read_csv("bus_data/bus_iat.csv")
bus_idt_df = pd.read_csv("bus_data/bus_idt.csv")
bus_info_df = pd.read_csv("bus_data/bus_info.csv")
df_list = [psn_iat_df, psn_idt_df, bus_iat_df, bus_idt_df]

env = simpy.Environment()
stations = [Station(env, f'S{i}', distance) for i, distance in enumerate(bus_iat_df['distance'])]
stations[-1].is_terminal = True
buses = [Bus(env, row, stations) for i, row in bus_info_df.iterrows()]

hour_summaries = [[], [], [], [], [], [], []]

env.process(dispatch_buses(env, bus_idt_df, buses))
env.process(dist_change(env, stations, buses, df_list))
env.process(monitor(env, stations, buses, hour_summaries))
env.run(until=SIM_TIME)

print(f'simulation end')

# statistics and cost calculation

daily_passengers = 0
daily_driving_time = 0
daily_driving_distance = 0
daily_fee = 0
daily_bus_cost = 0

for bus in buses:
    print(f'{bus.name} transported {bus.psn_cnt} passengers during {bus.driving_time} min')
    daily_passengers += bus.psn_cnt
    daily_driving_time += bus.driving_time
    daily_driving_distance += bus.driving_distance

for station in stations:
    if station.n_psn_renege > 0:
        print(f'{station.n_psn_renege} passengers reneged at {station.name}')

print(f'daily passengers: {daily_passengers}')
print(f'daily driving time: {daily_driving_time}')
print(f'daily driving distance: {daily_driving_distance} ')

df_columns = psn_idt_df.columns.drop(['station', 'average', 'std'])
csv_names = ['board', 'depart', 'renege', 'wait', 'bus users', 'drive time', 'drive distance']
for summary, filename in zip(hour_summaries, csv_names):
    summary_df = pd.DataFrame(np.transpose(np.array(summary)), columns=df_columns)
    file_dir = 'output/' + filename + '.csv'
    summary_df.to_csv(file_dir, sep=',')

# calculate total fee
age_fee_df = pd.read_csv('passenger_data/age_ratio_and_fee.csv')
for key, value in age_fee_df.iteritems():
    daily_fee += daily_passengers * value[0] * value[1]

print(f'daily fee: {round(daily_fee)}')

# calculate bus operating cost
large_bus_cost_df = pd.read_csv('bus_data/costs_large.csv')
small_bus_cost_df = pd.read_csv('bus_data/costs_small.csv')

for bus in buses:
    if bus.category == 'medium':
        bus.calculate_cost(small_bus_cost_df)
    else:
        bus.calculate_cost(large_bus_cost_df)

    print(f'{bus.name} operating cost : {bus.cost} won per day')
    daily_bus_cost += bus.cost

print(f'sum of daily bus operating cost: {daily_bus_cost}')
daily_profit = daily_fee - daily_bus_cost
print(f'daily profit: {round(daily_profit)}')
