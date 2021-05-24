import simpy
import random

NUM_BUSES = 8
NUM_SEATS = 40
SERVICE_MEAN = 5
SERVICE_STD = 0.5

ARRIVAL_RATE = 2
LEAVING_RATE = 2
SIM_TIME = 100

""" 정류장 정보 """
#Que_ride = [0]*9
#Que_out = [0]*9

Total_bus_count = 0
Total_customer_count = 0



Machine_service_time = [0]*NUM_BUSES
Server_Idles = [True]*NUM_BUSES

def time_to_Arrive():
    process_time = random.expovariate(ARRIVAL_RATE)
    return process_time

def time_to_Leave():
    process_time = random.expovariate(LEAVING_RATE)
    return process_time

def time_to_Move1():
    break_time = random.normalvariate(SERVICE_MEAN, SERVICE_STD)
    return break_time

def time_to_Move2():
    break_time = random.normalvariate(SERVICE_MEAN, SERVICE_STD)
    return break_time

class BusStops():
    def __init__(self,env,bus):
        self.env = env
        self.working = env.process(self.working(bus))
        self.Que_ride = [0]*3
        self.Que_out = [0]*3

    def working(self,Bus):
        global Total_bus_count

        while True:

            # yield self.env.timeout(process_time)

            with bus.request() as req:
                yield req
                """ 버스 탑승객수 """
                Bus_riding = 0

                """ 승하차 """
                Bus_riding = self.ride_and_out(Bus_riding,  0)
                """ 주행 """
                yield self.env.timeout(time_to_Move1())
                """ 승하차 """
                Bus_riding = self.ride_and_out(Bus_riding,  1)
                """ 주행 """
                yield self.env.timeout(time_to_Move2())
                Bus_riding = self.ride_and_out(Bus_riding, 2)

                Total_bus_count += 1



    def ride_and_out(self, Bus_riding, Stop_ID):
        global Total_customer_count
        """" 하차 """
        if Bus_riding - self.Que_out[Stop_ID] >= 0:   # 버스 탑승객이 하차인원보다 많으면
            Bus_riding -= self.Que_out[Stop_ID]
            self.Que_out[Stop_ID] = 0
        else:                                             # 버스 탑승객이 하차인원보다 적으면
            self.Que_out[Stop_ID] -= Bus_riding
            Bus_riding = 0

        """ 승차 """
        if Bus_riding + self.Que_ride[Stop_ID] <= NUM_SEATS: # 버스 남은자리가 승차인원보다 많으면
            Bus_riding += self.Que_ride[Stop_ID]
            Total_customer_count += self.Que_ride[Stop_ID]   # 전체 탑승인원에 추가
            self.Que_ride[Stop_ID] = 0
        else:                                             # 버스 남은자리가 승차인원보다 적으면
            self.Que_ride[Stop_ID] -= (NUM_SEATS -Bus_riding)
            Total_customer_count += (NUM_SEATS -Bus_riding)   # 전체 탑승인원에 추가
            Bus_riding = NUM_SEATS

        return Bus_riding



env = simpy.Environment()
bus = simpy.PreemptiveResource(env, capacity=NUM_BUSES)

BusStops(env, bus)

env.run(until=SIM_TIME)

print(Total_customer_count)
print(Total_bus_count)