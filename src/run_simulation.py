from bus_system import *
import numpy as np
import pandas as pd

n_days = 10

total_bus_idt_df = pd.read_csv("bus_data/bus_idt.csv")
n_cases = int(len(total_bus_idt_df.columns)/2)
final_results = [[], [], [], []]

best_case = -1
best_profit = -100000000
best_waiting_time = -1
best_renege = -1


for case in range(n_cases):

    total_profit = 0
    total_wating_time = 0
    total_renege = 0

    for day in range(n_days):
        print(f'-------------------- day {day + 1} --------------------')
        # system setup
        n_stations = 9
        time_zone = 18
        SIM_TIME = 60 * time_zone + 1

        psn_iat_df = pd.read_csv("passenger_data/psn_iat.csv")
        psn_idt_df = pd.read_csv("passenger_data/psn_idt.csv")
        bus_iat_df = pd.read_csv("bus_data/bus_iat.csv")
        # bus_idt_df = pd.read_csv("bus_data/bus_idt.csv")
        bus_idt_df = total_bus_idt_df.iloc[:, [2*case + 1, 2*case + 2]]
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
        daily_total_waiting_time = 0
        # daily_waiting_cost_waste = 0

        for bus in buses:
            print(f'{bus.name} transported {bus.psn_cnt} passengers during {bus.driving_time} min')
            daily_passengers += bus.psn_cnt
            daily_driving_time += bus.driving_time
            daily_driving_distance += bus.driving_distance

        for station in stations:
            if len(station.psn_waiting_time) > 0:
                daily_total_waiting_time += sum(station.psn_waiting_time)
            if station.n_psn_renege > 0:
                print(f'{station.n_psn_renege} passengers reneged at {station.name}')
                total_renege += station.n_psn_renege

        print(f'daily passengers: {daily_passengers}')
        print(f'daily driving time: {daily_driving_time}')
        print(f'daily driving distance: {daily_driving_distance}')

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

        print(f'daily fee: {round(daily_fee)} won')

        # calculate bus operating cost
        large_bus_cost_df = pd.read_csv('bus_data/costs_large.csv')
        small_bus_cost_df = pd.read_csv('bus_data/costs_small.csv')

        for bus in buses:
            if bus.category == 'medium':
                bus.calculate_cost(small_bus_cost_df)
            else:
                bus.calculate_cost(large_bus_cost_df)

            print(f'{bus.name} operating cost : {bus.cost} won')
            daily_bus_cost += bus.cost

        print(f'sum of daily bus operating cost: {daily_bus_cost} won')
        daily_profit = daily_fee - daily_bus_cost
        print(f'daily profit: {round(daily_profit)} won')
        total_profit += daily_profit

        print(f'sum of waiting time: {daily_total_waiting_time} minutes')
        daily_average_waiting_time = daily_total_waiting_time / daily_passengers
        print(f'daily average waiting time: {daily_average_waiting_time} minutes')
        total_wating_time += daily_average_waiting_time
        # daily_waiting_cost_waste = daily_total_waiting_time * 66.8379
        # net_profit = daily_profit - daily_waiting_cost_waste
        # print(f'net profit concidering wating time: {round(net_profit)}')

    average_profit = total_profit / n_days
    average_waiting_time = total_wating_time / n_days
    average_renege = total_renege / n_days
    print('')
    print(f'{n_days}days average profit: {average_profit} won')
    print(f'{n_days}days average waiting: {average_waiting_time} minutes')
    print(f'{n_days}days average renege: {average_renege}')

    # append results to final_results.csv
    final_results[0].append(case)
    final_results[1].append(average_profit)
    final_results[2].append(average_waiting_time)
    final_results[3].append(average_renege)

    if average_profit > best_profit:
        best_case = case
        best_profit = average_profit
        best_waiting_time = average_waiting_time
        best_renege = average_renege

print('')
print(f'best case : case{best_case}')
print(f'average profit: {best_profit} won')
print(f'average waiting: {best_waiting_time} minutes')
print(f'average renege: {best_renege}')

final_results[0].append('best : ' + str(best_case))
final_results[1].append(best_profit)
final_results[2].append(best_waiting_time)
final_results[3].append(best_renege)


# print final results to csv file
result_col = ['case', 'average profit', 'average wating time', 'average renege']
result_df = pd.DataFrame(np.transpose(np.array(final_results)), columns=result_col)
result_df.to_csv('output/final_results.csv', sep=',', index=False)