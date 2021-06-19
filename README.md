# SNU_DES_bus

## DONE
* 하루(6시~24시) 동안 시뮬레이션 후 통계치와 코스트 계산<br/>
* 버스, 정류장, 승객 모두 클래스로 구현<br/>
* 매 시간마다 승객, 버스 시간 분포 갱신<br/>
* 버스 종류, 연료 종류, 주행거리 따라서 일 버스 운용비를 계산<br/>
* 승객 수와 인구분포 통해서 일 이익을 계산<br/>
* 원하는 일 수 만큼 반복 시뮬레이션 후 평균 운영이익, 인당 대기시간, 평균 탑승포기인원, 일별 시간가치 고려 총 이익/손해 계산<br/>
* 원하는 배차강격 case 만큼 다시 반복<br/>
* 계산 결과를 csv로 정리 (/output)<br/>
* 원하는 csv 파일 양식만 맞추어 바꾸면 어느 노선이던지 원하는 노선과 버스종류, 배차간격 등 시뮬레이션 가능 (정류장 개수 상관 없음. 폴더별 readme 참고)<br/>
* 셔틀버스 등 공익 목적이면 대기시간 시간가치 계산값 사용가능 (발표는 미사용)<br/>

## INPUT
  csv파일<br/>
* bus_info.csv 파일에 버스의 이름, 종류, 연료, 차종, 용량 저장 후 이대로 버스 생성<br/>
* 최적화 위해 원하는 배차 간격을 bus_idt.csv에 입력하여 각 경우 별 수치들 계산<br/>
* 코로나 이전 이후 비교하고 싶으면 각 폴더의 승객 분포 데이터 복사해 사용가능<br/>
* 기타 아래 참고<br/>

전역변수<br/>
* n_days로 시뮬레이션 반복 일수 조절, 기본 10일, 발표는 100일기준<br/>
* cost_per_minute로 승객의 분당 시간 가치 환산금액 조절, 현재는 선행연구값<br/>
* discount로 세금 등 고려 이익에 곱하기, 현재는 0.8. 환승 고려할 때 사용가능<br/>
* waiting_limit로 승객의 인내심 조절, 기본 15분<br/>

## OUTPUT
* 계산 결과를 csv로 정리 (/output)<br/>
* 원하는 번호의 주석을 해제하면 원하는 출력을 볼 수 있음 (아래 참고)<br/>
* 현재 출력되는 내용은 각 case별 순이익, 대기시간, 탑승포기인원, 시간가치 합산결과<br/>
* Case별 상세한 결과는 각 폴더에 저장<br/>
* 최적화에 필요한 전체 결과는 final_result.csv에 저장<br/>

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
    
Input files
  bus_data 폴더
    bus_data_readme.txt: 설명
    bus_iat.csv: 구간별/시간대별 버스 이동시간
    bus_idt.csv: 시간대별 버스 배차간격 평균/표준편차, 원하는 경우만큼 여러 개 가능
    bus_info.csv: 생성할 버스의 이름, 종류, 연료, 차종, 용량 지정 차종 섞어도 가능, 단 대형버스는 large 중형버스는 medium 대소문자유의
    capacities.csv: 버스 차종별 용량 정보 참고용(bus_data_readme.txt참고)
    cost_large.csv: 대형버스 운용비용
    cost_small.csv: 중형버스 운용비용
  passenger_data 폴더 
    passenger_data_readme.txt: 설명
    age_ratio_and_fee.csv: 인구분포
    psn_iat.csv: 정류장별/시간대별 승차 대기열 방문 시간분포
    psn_idt.csv: 정류장별/시간대별 하차 대기열 추가 시간분포
  
Output files
  case별 폴더
    board.csv: 정류장/시간대별 탑승객 수
    depart.csv: 정류장/시간대별 하차객 수
    renege.csv: 정류장/시간대별 승차 포기 승객 수
    wait.csv: 정류장/시간대별 평균 대기 시간
    bus users.csv: 버스/시간대별 이용객 수
    drive distance.csv: 버스/시간대별 운행 거리 (종점 -> 시점 이동은 포함 X)
    drive time.csv: 버스/시간대별 운행 시간 (종점 -> 시점 이동은 포함 X)
  final_result.csv: 배차시간 case별 버스운영이익, 평균 대기시간, 평균 탑승포기 인원수, 시간가치 고려 총 이익/손해 

기타
  after_corona 폴더: 코로나 이후 승객 분포 파일(현재)
  before_corona 폴더: 코로나 이전 승객 분포 passenger_data 안에 덮어쓰기시 비교 가능
  
  
주석번호 
지우고 싶을 때 #과 숫자 함께 지우기
출력 내용이 굉장히 길어지고 속도가 느려지므로 필요한 것만 해제하거나 날짜수를 줄이길 추천
#1 버스 별 버스 출발 시각 출력. 배차간격이 시간에 따라 입력한 분포대로 변하는지 확인 가능
#2 버스 별 운행 종료 시각 출력. 운행 시간이 시간에 따라 입력한 분포대로 변하는지 확인 가능
#3 하루치 시뮬레이션 끝날 때마다 simulation end 출력
#4 하루 동안 각 버스가 몇 명을 몇 분 동안 태웠는지 출력
#5 하루 동안 각 정류장에서 승차 포기가 발생한 적이 있으면 몇 명이 포기했는지 출력
#6 하루 동안 총 탑승객 수 출력
#7 하루 동안 모든 버스의 운행시간 합 출력
#8 하루 동안 모든 버스의 운행거리 합 출력
#9 하루 동안 모든 버스가 벌어들인 이익 출력
#10 하루 동안 각 버스당 그 날의 운용 비용 출력
#11 하루 동안 모든 버스의 운용 비용 합 출력
#12 하루 동안 그 날의 순이익 출력
#13 하루 동안 전체 대기시간의 합 출력
#14 일평균 대기시간 출력
#15 하루치 대기시간의 시간가치 고려한 순이익 혹은 순손실 출력


```
