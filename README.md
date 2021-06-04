# SNU_DES_bus

## TODO
통계치 산출 방법 <br/>
* passenger waiting time
* bus driving time <br/>

실제 데이터 import 방법 (via csv / manual copy & paste) <br/>
import from csv <br/>

* psn_iat_dist_list: list of passenger arrival time distribution (mean, std) for each stations. <br/>
정류장 별 승차 인원 / 정류장에 도착하는 버스 시간 간격

* psn_idt_dist_list: list of passenger departure time distribution (mean, std) for each stations. <br/>
정류장 별 하차 인원 / 정류장에 도착하는 버스 시간 간격 <br/>

* bus_iat_dist_list: bus IAT distribution (mean, std) between stations <br/>
정류장 간 버스 운행 시간 <br/>

* bus_idt_dist: bus inter-dispatch time distribution (mean, std)<br/> 
버스가 system에 추가되는 시간 간격 <br/> 
총 버스 대수 / 적당한 시간 간격 <br/>

csv 읽어오는 몇줄 추가 <br/>
일단은 pandas로 csv 읽어온 다음 필요한 부분만 list로 변환 <br/>
현재는 psn은 각 정류장별 일일 전체 평균값만 사용, 작동하는지 확인만 <br/>
bus도 마찬가지로 마지막 행 또는 열에 일일 전체 평균 추가하여 사용 <br/>
bus_idt는 정류장 상관없이 차고지에서 출발시만 필요하니 한줄만 남기고 지움, 행열 바꿔서 읽기 쉽게 <br/>
시간대별로 바뀌는건 시험 뒤에? 방식은 고민중 <br/>

버스 클래스에 driving time 추가 <br/>
total passengers, total driving time 추가 <br/>

### word definition and miscellaneous guide

```
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

naming rule:
    Bus: B{i}
    Station: S{i}
    Passenger: S{i}P{j}: station[i]의 j번째 passenger

simpy.Store() class
items: list of items
capacity: Maximum capacity
put(): request to put a/many item(s) in store
get(): request to get an item in store
put(), get()은 request 이므로 yield 할 시에 함수가 실행될 때 까지 진행되지 않음
store 의 capacity 가 무한하면 yield put() 을 해도 아무 문제 없음.
그러나 빈 store 에서 yield get() 을 할 경우 코드 진행이 멈춤에 주의


```
