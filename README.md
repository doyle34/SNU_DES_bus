# SNU_DES_bus
profit optimization for n_bus = 5
## Functions
* 하루(6시~24시) 동안 시뮬레이션 후 통계치와 코스트 계산<br/>
* 매 시간마다 승객, 버스 시간 분포 갱신<br/>
* 매 시간마다 정류장 별 평균 승차 대기 시간 계산 후 daily_waiting_times.csv에 저장<br/>
* bus_info.csv 파일에 버스의 이름, 종류, 연료, 모델, 용량 저장하고 이로부터 버스 생성<br/>
* 일 버스 요금과 버스 운용비를 계산하고 일 이익을 계산
* 100일간의 통계치와 코스트 계산 <br/>
* 계산 결과를 csv로 정리 (/output)

## Optimization Strategy
하루 중 운행 시간대를 탑승 인원 분포에 맞추어 분류한다 </br>
* sparse: 5, 6, 22, 23 <br/>
* normal: 7, 10, 11, 12, 13, 14 ,15, 16, 20, 21 <br/>
* peak: 8, 9, 17, 18, 19 <br/>

각 운행 시간대별로 버스 배차 간격을 조금씩 조정하여 case study </br>
profit이 최대가 되는 case를 구한다 </br>

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
    
output files
    board.csv: 정류장/시간대별 탑승객 수
    depart.csv: 정류장/시간대별 하차객 수
    renege.csv: 정류장/시간대별 승차 포기 승객 수
    wait.csv: 정류장/시간대별 평균 대기 시간
    bus users.csv: 버스/시간대별 이용객 수
    drive distance.csv: 버스/시간대별 운행 거리 (종점 -> 시점 이동은 포함 X)
    drive time.csv: 버스/시간대별 운행 시간 (종점 -> 시점 이동은 포함 X)

```
