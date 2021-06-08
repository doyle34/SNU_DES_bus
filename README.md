# SNU_DES_bus

## TODO
이틀 이상의 시뮬레이션 기간 동안의 통계치와 코스트 계산 <br/>
계산 결과를 csv로 정리
## DONE
하루(6시~24시) 동안 시뮬레이션 후 통계치와 코스트 계산

### word definition and miscellaneous guide

```
passenger == psn: 승객
passenger inter-arrival time == psn_iat: 승객이 정류장의 승차 대기열에 도착하는 시간 간격
mean: csv에서 읽어온 값 / sd: 0.01
passenger inter-departure time == psn_idt: 승객이 정류장의 하차 대기열에 추가되는 시간 간격
mean: csv에서 읽어온 값 / sd: 0.01
bus inter-arrival time == bus_iat: 버스가 정류장 사이를 운행하는 시간 간격
mean: csv에서 읽어온 값 / sd: 0.1
bus inter-dispatch time == bus_idt: 버스가 처음에 시스템에 추가되는 시간 간격이자 종점에서 시점으로 되돌아가는 시간
mean, sd: csv에서 읽어온 값
bus information == bus_info: 버스 이름, 종류, 모델, capacity

naming rule:
    Bus: bus_info.csv의 'name' column 값
    Station: S{i}
    Passenger: S{i}P{j}: station[i]의 j번째 passenger

```
