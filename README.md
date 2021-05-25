# SNU_DES_bus

## TODO
변수명 정리
시뮬레이션이 돌아가는지 확인해보기 (코드오류는없음)

### word definition

```passenger == psn```: 승객 <br/>
```passenger arrival time == psn_arrival_time == psn_arr_t```: 승객이 정류장의 승차 대기열에 도착하는 시간 간격 <br/>
```passenger getoff time == psn_getoff_time == psn_off_t```: 승객이 정류장의 하차 대기열에 추가되는 시간 간격 <br/>
```bus_IAT```: 버스가 정류장 사이를 운행하는 시간 간격 <br/>
```(name)_dist```: (name)의 distribution 정보를 담음. 보통 정규분포의 평균과 표준편차. <br/>
    ex) ```psn_arr_t_dist``` 는 ```psn_arr_t``` 의 분포 정보를 담고 있음. ```np.array([mean, std])``` 형식. <br/>
```(name)_list```: (name)의 python list. numpy array 와 다름 <br/>
    ex) ```psn_arrival_time_dist_list``` 는 ```psn_arrival_time_dist``` 의 list.
    ```psn_arrival_time_dist``` 는 ```np.array([mean, std])``` 형식 이므로
    ```psn_arrival_time_dist_list``` 는 ```list(np.array([mean, std]))``` 형식임
