---
title: 기본 명령어4
author: 노아
date: 2024-09-20 12:12:00 +0800
categories: [Linux, 기본 명령어, 기본 명령어4]
tags: [리눅스, 기본 명령어4]
pin: true
math: true
mermaid: true

---
기본 명령어4
- 기타 명령어

# 목차

- 네트워크 관련 명령어
- 기타 명령어

# 네트워크 관련 명령어
- ping
  - 네트워크에 연결된 호스트와 호스트 간의 연결 상태를 확인하는 명령어.
  - 옵션 지정이 없는 경우 연속적으로 명령을 실행함.
  - 기본 형식

```
root@noah-VirtualBox:~$ ping [옵션] [IP 주소/도메인]

ex>
noah@noah-VirtualBox:~$ ping -c 3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 바이트 (8.8.8.8에서): icmp_seq=1 ttl=115 시간=42.9 ms
64 바이트 (8.8.8.8에서): icmp_seq=2 ttl=115 시간=42.4 ms
64 바이트 (8.8.8.8에서): icmp_seq=3 ttl=115 시간=63.9 ms

--- 8.8.8.8 핑 통계 ---
3 패킷이 전송되었습니다, 3 수신되었습니다, 0% 패킷 손실, 시간 2003ms
rtt 최소/평균/최대/표준편차 = 42.445/49.731/63.898/10.018 ms
```

> **참조** 
> - TTL(Time to live)
>   - 목표에 도달하지 못할 시 이 패킷이 네트워크 상을 돌아다니는 걸 방지하기 위해 생존 값을 준 것.
>   - 기본 값 : 64(Red hat: 255, cisco: 255, Debian: 64, solaris: 128, ms windows: 128)
>   - 라우터 하나 거칠 때마다 TTL 값 하나씩 소멸됨.
>
> - cmp_seq : 패킷 일련번호
>
> - ipg : 패킷 간의 간격. 하나의 패킷 처리하고 다음 패킷까지 가는데 걸리는 시간
>
> - ewma : 최근 데이터 지점에서 더 높은 가중치를 주는 인자를 사용하여 계산하는 것.
>
> - icmp : tcp/ip 프로토콜 제품군의 일부로 업데이트 및 오류 메시지를 보내는데 사용되며, 패킷 전달 실패와 같은 네트워크 문제를 디버깅하는데 사용되는 유용한 프로토콜(프로토콜 : 컴퓨터 내부/사이에서 데이터 교환 방식을 정의하는 규칙 체계)

- traceroute
  - 목적지 호스트까지 경로를 출력하고, 그 정보를 기록하는 명령어.
  - 목적지 호스트까지 경로에서 장애 구간을 파악할 수 있음.
  - 기본 형식

```
root@noah-VirtualBox:~$ traceroute [옵션] [IP 주소/도메인]

ex>
noah@noah-VirtualBox:~$ traceroute 192.168.~
traceroute to 192.168.~ (192.168.~), 30 hops max, 60 byte packets
 1  _gateway (~~)  0.904 ms  0.822 ms  0.803 ms
 2  _gateway (~~)  5.166 ms  5.142 ms  4.975 ms
```

> **참조**
> - 홉 : 거치게 되는 라우터의 수로 징검다리 같은 것. 데이터 통신망에서 각 패킷이 매 노드(or 라우터)를 건너가는 양상을 비유적으로 표현.
> - 다음 홉 : 목적지까지 가기 위한 다음의 라우터.

- nslookup
  - 도메인 이름으로 IP 주소를 조회하거나 IP 주소로 도메인 이름을 조회하는 명령어.[네트워크 디버깅]
  - 기본 형식

```
root@noah-VirtualBox:~$ nslookup [-type=record] [IP 주소/도메인]

ex>
noah@noah-VirtualBox:~$ nslookup 8.8.8.8
8.8.8.8.in-addr.arpa	name = dns.google.

Authoritative answers can be found from:
```

- dig
  - Domain Information Groper의 약어로 nslookup 명령어와 유사하며, 도메인 이름으로 IP 주소를 조회하거나 IP 주소로 도메인 이름을 조회하는 명령어.
  - DNS 서버 구성과 도메인 설정이 완료된 후, 사용자 입장에서 설정한 도메인 이름에 대한 DNS 질의 응답이 정상적으로 이루어지는지를 확인 점검하는 경우에 많이 사용함.
  - 기본 형식

```
root@noah-VirtualBox:~$ dig [@server] [query-type] [query-class]

## @server -> 특정 DNS 서버에 쿼리를 보내고자 할 때 사용함.

ex>
noah@noah-VirtualBox:~$ dig naver.com

; <<>> DiG 9.16.48-Ubuntu <<>> naver.com
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 26946
;; flags: qr rd ra; QUERY: 1, ANSWER: 4, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 65494
;; QUESTION SECTION:
;naver.com.			IN	A

;; ANSWER SECTION:
naver.com.		277	IN	A	223.130.200.219
naver.com.		277	IN	A	223.130.192.248
naver.com.		277	IN	A	223.130.200.236
naver.com.		277	IN	A	223.130.192.247

;; Query time: 12 msec
;; SERVER: 127.0.0.53#53(127.0.0.53)
;; WHEN: Tue Oct 01 16:12:56 KST 2024
;; MSG SIZE  rcvd: 102
```

- host
  - DNS 서버를 이용하여 도메인 이름에 대한 IP 주소를 조회하는 명령어.
  - 호스트 이름을 이용하면 하위 도메인도 조회 가능.
  - 기본 형식

```
root@noah-VirtualBox:~$ host [옵션] [도메인/IP 주소] [DNS 서버]

ex>
noah@noah-VirtualBox:~$ host naver.com
naver.com has address 223.130.192.248
naver.com has address 223.130.200.219
naver.com has address 223.130.192.247
naver.com has address 223.130.200.236
naver.com mail is handled by 10 mx2.naver.com.
naver.com mail is handled by 10 mx3.naver.com.
naver.com mail is handled by 10 mx1.naver.com.
```

- hostname
  - 호스트 이름을 확인하거나 변경하는 명령어.
  - 기본 형식

```
noah@noah-VirtualBox:~$ hostname [옵션] [파일 명]
 
ex>
noah@noah-VirtualBox:~$ hostname 
noah-VirtualBox
```


# 기타 명령어
- date
  - 시스템의 날짜 출력하거나 변경하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ date [옵션] [MMDDhhmm][CC][YY][.ss] 또는 date [옵션] +FORMAT

ex> 
noah@noah-VirtualBox:~$ date
2024. 10. 01. (화) 16:32:03 KST
```

- rdate
  - 원격지의 타임 서버에서 시간 정보를 가져와 로컬 시스템의 시간과 동기화하는 명령어.
  - 기본 형식

  ```
  root@noah-VirtualBox:~$ rdate [옵션] [타임 서버 IP 주소/도메인]
  ```

- cal
  - 달력을 출력하는 명령어
  - 기본 형식

  ```
    root@noah-VirtualBox:~$ cal
  ```

  - time
    - 프로그램 실행 시간을 출력하는 명령어

- tty
  - 현재 사용하고 있는 단말 장치의 경로와 파일명을 출력함.

```
ex>
noah@noah-VirtualBox:~$ tty
~~
```

- clear 
  - 터미널 화면을 모두 지우는 명령어

```
ex>
noah@noah-VirtualBox:~$ clear
noah@noah-VirtualBox:~$ 
```

- wall
  - 현재 로그인된 모든 사용자에게 터미널을 통해 메시지를 전송하는 방식.

```
ex>
noah@noah-VirtualBox:~$ wall "tello"
                                                                               
Broadcast message from noah@noah-VirtualBox (pts/0) (Tue Oct  1 16:39:42 2024):
                                                                               
tello
                                                                               
noah@noah-VirtualBox:~$ 
```

- write
  - 지정된 사용자에게만 메시지를 전송하는 명령어.
  - 행 단위로 다른 사용자와의 의사소통을 할 수 있도록 함.

```
noah@noah-VirtualBox:~$ write [사용자 명] [tty 명]
```

- MESG
  - mesg 명령은 메시지 수신 여부를 확인하고 제어하는 명령어.
  - ```noah@noah-VirtualBox:~$ mesg [y/n]```