import simpy
import math
import numpy as np
from random import normalvariate

WAITING_LIMIT = 15  # Maximum waiting time of a passenger


class Bus:
    """Bus class for DES simulation.

    Attributes
    ----------
    env : simpy.Environment
        Simpy environment where this bus is created.
    name : str
        Name of bus.
    category : str
        Category of bus. This should be one of { 'large', 'middle' }
    fuel : str
        Fuel type which this bus uses. One of { 'CNG', 'H2' }
    model : str
        Model name of bus. (ex: 'New_Super_Aerocity')
    cost : float
        Daily operation cost including fuel cost
    stations : list
        List of bus_system.Station. Bus drives along these stations.
    bus_idt_dist : numpy.ndarray
        Normal distribution parameter for bus inter-dispatch time.
        numpy.array([mean, std])
    passengers : simpy.store
        FIFO queue modeled by simpy.Store class.
        capacity is the maximum number of passengers a bus can contain.
    board_cnt : int
        Total number of passengers boarded on a bus.
    leave_cnt : int
        Total number of passengers got off a bus.
    driving_time : float
        Total bus driving time not including terminal to
    driving_distance : float
        Total bus driving distance.
    driving_process : simpy.events.Process
        Simpy process which triggered when a bus is dispatched and starts driving.
    running : simpy.Resource
        Simpy basic resource to prevent error that a bus is dispatched before it even finishes driving.

    """
    def __init__(self, env, bus_info, stations):
        """
        :param env: simpy.Environment where a bus is created.
        :param bus_info: pandas.Series which contains information for a bus
        :param stations: list of stations which a bus drives
        """
        self.env = env
        self.name = bus_info["name"]
        self.category = bus_info["category"]
        self.fuel = bus_info["fuel"]
        self.model = bus_info["model"]
        self.cost = 0
        self.stations = stations
        self.bus_idt_dist = np.array([13.5, 2.475])
        self.passengers = simpy.Store(self.env, capacity=bus_info["capacity"])
        self.board_cnt = 0
        self.leave_cnt = 0
        self.driving_time = 0
        self.driving_distance = 0
        self.driving_process = 0
        self.running = simpy.Resource(self.env, capacity=1)

    def arrive(self, station):
        """Function called when a bus arrives at the station.

        When a bus arrives at the station, passengers in the bus get off first.
        If the station is terminal, all passengers get off.
        Otherwise, the number of passengers getting off is determined by the station's departing queue length.
        After passengers in the bus get off, passengers in the station's boarding queue start boarding.
        If a bus is full, half of passengers in the boarding queue renege.
        Even if a bus is not full, passengers who waited more than WAITING_LIMIT minutes renege.

        :param station: Bus arrives at this station.
        """
        # bus arrives at a station, and passengers get off
        temp_cnt = 0
        if station.is_terminal:  # if bus arrived at terminal
            for i in range(station.n_psn_depart):
                if self.passengers.items:
                    yield self.passengers.get()
                    temp_cnt += 1

            while self.passengers.items:
                yield self.passengers.get()
                self.leave_cnt += 1

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
                    passenger_renege = yield station.boarding_queue.get()  # half of passengers renege
                    passenger_renege.end_waiting(self.env)
                    passenger_renege.renege()
                    station.psn_waiting_time.append(passenger_renege.waiting_time)
                    station.n_psn_renege += 1

                break  # forced while loop exit

            else:  # if bus is not full
                passenger_now = yield station.boarding_queue.get()
                passenger_now.end_waiting(self.env)
                if passenger_now.waiting_time > WAITING_LIMIT:  # passenger renege if waited too long
                    passenger_now.renege()
                    station.psn_waiting_time.append(WAITING_LIMIT)
                    station.n_psn_renege += 1

                else:
                    station.psn_waiting_time.append(passenger_now.waiting_time)
                    yield self.passengers.put(passenger_now)
                    temp_cnt += 1
                    self.board_cnt += 1

        station.n_hr_psn_board += temp_cnt

    def drive(self):
        """Function called when a bus starts driving.

        First, validate if a bus is driving already. This is done by yielding a request in simpy resource.
        Then, a bus yields driving time to next station and add its driving time and distance
        After yielding driving time, a bus arrives at a station by calling self.arrive function.
        After iterating driving and arriving process, a bus ends driving for a cycle and
        wait until next dispatch.

        """
        with self.running.request() as req:
            yield req
# 1         print(self.name + ' start driving at ' + str(self.env.now))
            for station in self.stations:
                driving_time_single = normalvariate(station.bus_iat_dist[0], station.bus_iat_dist[1])
                yield self.env.timeout(driving_time_single)  # bus moves to next station
                self.driving_time += driving_time_single
                self.driving_distance += station.distance
                yield self.env.process(self.arrive(station))  # bus arrives at station[i]
            # bus finishes driving for one cycle
# 2         print(self.name + ' finish driving at ' + str(self.env.now))
            real_dispatch_time = max(normalvariate(self.bus_idt_dist[0], self.bus_idt_dist[1])
                                     - normalvariate(self.stations[0].bus_iat_dist[0],
                                                     self.stations[0].bus_iat_dist[1]), 0)
            yield self.env.timeout(real_dispatch_time)
            # print(self.name + ' ready at ' + str(self.env.now))

    def calculate_cost(self, bus_cost):
        """Calculate operating cost including fuel cost of a bus.

        :param bus_cost: pandas.DataFrame that contains bus cost information.
        """
        fuel_cost = bus_cost[self.fuel]
        operation_cost = bus_cost['operational']
        retain_cost = bus_cost['retain']
        self.cost = int(fuel_cost * self.driving_distance + operation_cost + retain_cost)
        # print(f'total bus cost: {total_bus_cost}')

    def dispatch(self):
        """Function called periodically to dispatch a bus.

        This function trigger driving process. With process triggered, bus starts driving
        for a cycle by calling self.drive function.

        :return:
        """
        self.driving_process = self.env.process(self.drive())


class Station:
    """Station class for DES simulation.

    Attributes
    ----------
    env : simpy.Environment
        Simpy environment where this station is created.
    name : str
        Name of a station. (ex: 'S0', 'S1')
    distance : float
        Distance from previous station to current station.
    is_terminal : bool
        True only if a station is terminal. False otherwise.
    boarding_queue : simpy.Store
        FIFO queue modeled by simpy.Store class. Assume infinite capacity.
    psn_iat_dist : numpy.ndarray
        Normal distribution parameters of passenger inter-arrival time.
        numpy.array([mean, std])
    psn_idt_dist : numpy.ndarray
        Normal distribution parameters of passenger inter-departure time.
        numpy.array([mean, std])
    bus_iat_dist : numpy.ndarray
        Normal distribution parameters of bus inter-arrival time.
        numpy.array([mean, std])
    n_psn_depart : int
        Number of passengers in a station's departing queue.
    n_psn_renege : int
        Total number of passengers reneged at a station.
    n_hr_psn_board: int
        Number of passengers boarded at a station during one hour.
    n_hr_psn_depart: int
        Number of passengers got off at a station during one hour.
    psn_waiting_time: list[float]
        List of waiting time of passengers.
    arrival_process : simpy.events.Process
        Simpy process triggered when a station is initialized.
    departure_process : simpy.events.Process
        Simpy process triggered when a station is initialized.

    """
    def __init__(self, env, name, distance):
        """
        :param env: simpy.Environment where a bus is created.
        :param name: Name of a station.
        :param distance: Distance from previous station to current station.
        """
        self.env = env
        self.name = name
        self.distance = distance  # distance 'to' current station
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
        """Yield passenger IAT, generate passengers and put them in boarding queue continuously.

        """
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
        """Yield passenger IDT and put them in departing queue continuously.

        """
        while True:
            yield self.env.timeout(normalvariate(self.psn_idt_dist[0], self.psn_idt_dist[1]))
            # new passenger wants to get off at this station
            self.n_psn_depart += 1


class Passenger:
    """Passenger class for DES simulation.

    Note
    ----
    Passenger class is actually not fully object-oriented. Due to absence of passenger travel data,
    passenger class can't simulate number of stations a passenger traveled.

    Attributes
    ----------
    name : str
        Passenger name. (for example, S2P013 means 13th passenger who arrived at station 2)
    waiting_start : float
        When a passenger started waiting in boarding queue.
    waiting_end : float
        When a passenger ended waiting in boarding queue.
        A passenger ends waiting if one of three conditions is true:
            1. board on a bus
            2. renege due to full seat
            3. renege due to reaching maximum waiting time
    waiting_time : float
        Waiting time of a passenger. same as (waiting_end - waiting_start)
    reneged : bool
        True if a passenger reneged.
    """
    def __init__(self, name):
        """
        :param name: Name of passenger
        """
        self.name = name
        self.waiting_start = 0
        self.waiting_end = 0
        self.waiting_time = 0
        self.reneged = False

    def start_waiting(self, env):
        """Passenger start waiting for a bus.

        :param env: simpy.Environment where simulation takes place.
        """
        self.waiting_start = env.now

    def end_waiting(self, env):
        """Passenger end waiting for a bus.

        :param env: simpy.Environment where simulation takes place.
        """
        self.waiting_end = env.now
        self.waiting_time = self.waiting_end - self.waiting_start

    def renege(self):
        """Passenger renege.
        """
        self.reneged = True


def dispatch_buses(env, bus_idt_df, buses):
    """Yield bus IDT time and dispatch buses continuously.

    :param env: simpy.Environment where simulation takes place.
    :param bus_idt_df: pandas.DataFrame which contains information for bus IDT.
    :param buses: List of buses.
    """
    while True:
        for bus in buses:
            j = min(math.floor(env.now / 60), len(bus_idt_df)-1)
            bus.dispatch()
            yield env.timeout(normalvariate(bus_idt_df.iloc[j, 0], bus_idt_df.iloc[j, 1]))


def dist_change(env, stations, buses, df_list):
    """Change time distribution of passengers and buses every hour during simulation.

    :param env: simpy.Environment where simulation takes place.
    :param stations: List of stations.
    :param buses: List of buses.
    :param df_list: List of pandas.Dataframe which contains time distribution of passengers and buses.
    """
    time_zone = 18
    psn_iat_df, psn_idt_df, bus_iat_df, bus_idt_df = df_list
    while True:
        for j in range(time_zone):
            for i, station in enumerate(stations):
                station.psn_iat_dist = np.array([psn_iat_df.iloc[i, j + 1], 0.01])
                station.psn_idt_dist = np.array([psn_idt_df.iloc[i, j + 1], 0.01])
                station.bus_iat_dist = np.array([bus_iat_df.iloc[i, j + 1], 0.1])

            for bus in buses:
                bus.bus_idt_dist = np.array([bus_idt_df.iloc[j, 0], bus_idt_df.iloc[j, 1]])

            yield env.timeout(60)


def monitor(env, stations, buses, hour_summaries):
    """Calculate statistics every hour and append them to list.

    :param env: simpy.Environment where simulation takes place.
    :param stations: List of stations.
    :param buses: List of buses.
    :param hour_summaries: List of hourly summarized data.
    """

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
            psn_cnt = bus.board_cnt - prev_cnt[i]
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
