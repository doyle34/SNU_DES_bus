# SNU_DES_bus

## TODO
* 이틀 이상의 시뮬레이션 기간 동안의 통계치 출력 <br/>
## DONE
* 하루(6시~24시) 동안 시뮬레이션 후 통계치와 코스트 계산<br/>
* 매 시간마다 승객, 버스 시간 분포 갱신<br/>
* 매 시간마다 정류장 별 평균 승차 대기 시간 계산 후 daily_waiting_times.csv에 저장<br/>
* bus_info.csv 파일에 버스의 이름, 종류, 연료, 모델, 용량 저장하고 이로부터 버스 생성<br/>
* 일 버스 요금과 버스 운용비를 계산하고 일 이익을 계산
* 원하는 일 수 만큼 반복 시뮬레이션 후 평균 일별 운영이익, 인당 대기시간, 일별 탑승포기인원, 일별 시간가치 고려 총 이익/손해 계산
* 최적화 위해 원하는 배차 간격을 bus_idt.csv에 입력하여 각 경우별 수치들 계산
* 계산 결과를 csv로 정리 (/output)

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
    final_result.csv: 배차시간 case별 버스운영이익, 평균 대기시간, 평균 탑승포기 인원수, 시간가치 고려 총 이익/손해 

```
