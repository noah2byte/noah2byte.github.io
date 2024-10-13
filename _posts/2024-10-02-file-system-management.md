---
title: 사용자 권한 및 그룹 설정
author: 노아
date: 2024-10-02 20:10:00 +0800
categories: [Linux, 파일 시스템 관리, 사용자 권한 및 그룹 설정]
tags: [리눅스, 사용자 권한 및 그룹 설정]
pin: true
math: true
mermaid: true

---
파일 시스템 관리
- 사용자 권한 및 그룹 설정

# 목차

- 파일 및 디렉터리의 속성
- 소유권 관련 명령어
- 허가권 관련 명령어
- 특수 허가권
- 디스크 쿼터(Disk Quota)

# 파일 및 디렉터리의 속성

- 모든 파일과 디렉터리에는 허가권(Permission)과 소유권(Ownership)이 부여된다. 이번 포스팅에서는 이러한 허가권과 소유권과 관련한 내용을 다룰 것이다. 리눅스 파일 시스템에서 아래와 같은 형태를 많이 봐왔을 것이다.

```drwxrwxr-x  2 noah noah 4096 10월  1 13:16 test33/```

여기서 이 각각은 어떠한 내용을 품고 있을까? 이를 위해 위의 형태를 아래와 같이 쪼개서 나타내보았다. 

d | rwxrwxr-x | 2 | noah | noah | 4096 | 10월  1 13:16 | test33/ |

이 각각은 어떠한 내용을 담고 있는 걸까? 이에 대해 하나씩 살펴보자면 아래와 같이 정리할 수 있을 것이다.

d | 파일 유형 |  |
 | - : 일반 파일
 | l : 심볼릭 링크 파일 |
 | d : 장치 파일 (디렉터리) |
 | p : 파이프 |
 | c : 문자 파일 |
 | b : 블록 장치 파일 |
 | s : 소켓 |
rwxrwxr-x | 허가권 - *하단 설명 |
2 | 링크 수 |
noah | 소유자명 |
noah | 그룹명 |
4096 | 파일 크기 |
10월  1 13:16 | 마지막으로 변경된 시간 |
test33/ | 파일명 |

위 표에서 rwxrwxr-x 부분인 허가권에 대해 추가 설명을 진행한다. 파일 유형 다음에 나오는 이 9개의 문자는 3씩 나누어 소유자, 그룹, 기타 사용자의 권한을 나타낸다고 볼 수 있는데, 그 전에 사용자 종류와 권한 종류에 대해 간단히 정리해보겠다.

- 사용자 종류
  - 소유자(owner) : 파일을 생성한 사용자
  - 그룹(group) : 파일이 속한 그룹에 속하는 사용자
  - 기타 사용자(other) : 소유자와 그룹에 속하지 않는 모든 사용자

- 권한 종류
  - 읽기(read, r) : 파일 내용을 읽을 수 있음. 디렉터리에서는 디렉터리 내 파일 목록을 볼 수 있음.
  - 쓰기(write, w) : 파일 내용을 수정하거나 삭제할 수 있음. 디렉터리에서는 파일을 추가, 삭제할 수 있음.
  - 실행(execute, x) : 파일을 실행할 수 있음. 디렉터리에서는 디렉터리에 접근할 수 있음.

그렇다면, 다시 위에서 언급했던 ```rwxrwxr-x```에 대해 해석해보자면, 각각 소유자는 r, w, x 권한 모두 가지고 있으며, 그룹 또한 r, w, x 모든 권한을 가지고 있으나, 기타 사용자의 경우, r, x 권한만 가지고 있다는 걸 의미한다고 할 수 있다. 

그러나, chmod 명령어로 권한을 변경할 때, 숫자로 설정할 수도 있다. 숫자로 설정하는 방법은 아래와 같다.

r = 4, w = 2, x = 1로 계산하여 합산.

예를 들어, ```chmod 755 example.txt```의 소유자는 rwx(4+2+1=7), 그룹은 r-x(4+1=5), 기타 사용자는 r-x(4+1=5)로 설정한다. 또한, 기호로 설정할 수도 있다. 기호로 사용할 시, u(소유자), g(그룹), o(기타 사용자)와 +, -, =을 사용한다. 각각에 대한 내용은 아래와 같다.

```+``` : 허가권 부여<br>
```-``` : 허가권 제거<br>
```=``` : 허가권 지정<br>

예를 들어 ```chmod u+x example.txt```를 사용하여 소유자에게 실행 권한을 추가할 수도 있다.


# 소유권 관련 명령어

- chown
  - 파일이나 디렉터리의 사용자 소유권과 그룹 소유권을 변경하는 명령어이다.
  - 파일이나 디렉터리의 사용자 소유권과 그룹 소유권을 한번에 변경할 수 있다.
  - 그리고 이때, root 사용자를 통해서만 소유권 변경이 가능하다.
  - 기본 형식

```
root@noah-VirtualBox:/home/noah/noah-test# chown [옵션] [사용자 명][:[그룹]] [파일/디렉터리명]

ex>
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 12
drwxr-xr-x 3 root root 4096 10월  6 23:09 ./
drwxrwxr-x 5 noah noah 4096 10월  6 23:09 ../
drwxr-xr-x 2 root root 4096 10월  6 23:09 noah2-test/
root@noah-VirtualBox:/home/noah/noah-test/test4# chown noah:noah noah2-test
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 12
drwxr-xr-x 3 root root 4096 10월  6 23:09 ./
drwxrwxr-x 5 noah noah 4096 10월  6 23:09 ../
drwxr-xr-x 2 noah noah 4096 10월  6 23:09 noah2-test/

root@noah-VirtualBox:/home/noah/noah-test/test4# chown :noah2 noah2-test
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 16
drwxr-xr-x 4 root root  4096 10월  6 23:10 ./
drwxrwxr-x 5 noah noah  4096 10월  6 23:09 ../
drwxr-xr-x 2 noah noah2 4096 10월  6 23:09 noah2-test/
drwxr-xr-x 2 root root  4096 10월  6 23:10 nosh3-test/
```

- chgrp
  - 파일이나 디렉터리의 그룹 소유권을 변경하는 명령어이다.
  - 기본 형식

```
root@noah-VirtualBox:/home/noah/noah-test/test4# chgrp [옵션] [그룹명] [파일/디렉터리명]

ex>
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 16
drwxr-xr-x 4 root root  4096 10월  6 23:10 ./
drwxrwxr-x 5 noah noah  4096 10월  6 23:09 ../
drwxr-xr-x 2 noah noah2 4096 10월  6 23:09 noah2-test/
drwxr-xr-x 2 root root  4096 10월  6 23:10 nosh3-test/
root@noah-VirtualBox:/home/noah/noah-test/test4# chgrp noah noah2-test
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 16
drwxr-xr-x 4 root root 4096 10월  6 23:10 ./
drwxrwxr-x 5 noah noah 4096 10월  6 23:09 ../
drwxr-xr-x 2 noah noah 4096 10월  6 23:09 noah2-test/
drwxr-xr-x 2 root root 4096 10월  6 23:10 nosh3-test/

```


# 허가권 관련 명령어

- chmod
  - 파일이나 디렉터리의 허가권을 변경하는 명령어로, 구체적으로는 파일과 디렉터리에 대한 읽기(read), 쓰기(write), 실행(execute) 권한을 사용자, 그룹, 기타 사용자에 대해 각각 설정할 수 있다.
  - 기본 형식

```
root@noah-VirtualBox:/home/noah/noah-test/test4# chmod [옵션] [허가권] [파일/디렉터리명]

ex>
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 16
drwxr-xr-x 4 root root 4096 10월  6 23:10 ./
drwxrwxr-x 5 noah noah 4096 10월  6 23:09 ../
drwxr-xr-x 2 noah noah 4096 10월  6 23:09 noah2-test/
drwxr-xr-x 2 root root 4096 10월  6 23:10 nosh3-test/
root@noah-VirtualBox:/home/noah/noah-test/test4# chmod 775 nosh3-test
root@noah-VirtualBox:/home/noah/noah-test/test4# ll
합계 16
drwxr-xr-x 4 root root 4096 10월  6 23:10 ./
drwxrwxr-x 5 noah noah 4096 10월  6 23:09 ../
drwxr-xr-x 2 noah noah 4096 10월  6 23:09 noah2-test/
drwxrwxr-x 2 root root 4096 10월  6 23:10 nosh3-test/

```

- umask
  - 리눅스/유닉스 시스템에서 기본 파일 및 디렉터리 권한을 설정하는데 사용되는 명령어.
  - 새로 생성되는 파일이나 디렉터리 권한을 결정하는 마스크 값을 설정하며, 사용자가 파일이나 디렉터리를 생성할 때 적용된다.
  - 기본 개념
    - 파일 권한 : 새로 생성된 파일의 기본 권한은 일반적으로 666 (읽기 및 쓰기 권한)이다.
    - 디렉터리 권한 : 새로 생성된 디렉터리의 기본 권한은 777 (읽기, 쓰기 및 실행 권한)이다.
    - umask : 사용자가 설정한 umask 값은 새로 생성되는 파일이나 디렉터리에 적용될 기본 권한에서 빼주는 형태로 작동함.
  - 기본 형식

```
root@noah-VirtualBox:/home/noah/noah-test/test4# umask [옵션] [설정값]

ex>
## umask 설정값 확인 -> umask
root@noah-VirtualBox:/home/noah/noah-test/test4# umask
0022
root@noah-VirtualBox:/home/noah/noah-test/test4# umask 027
root@noah-VirtualBox:/home/noah/noah-test/test4# umask
0027
```

  - 작동 원리
    - umask의 계산 방법 : 새로 생성된 파일이나 디렉터리의 기본 권한에서 umask 값을 빼준다. 
      - 예를 들어, 디폴트 권한이 777인 디렉터리에서 umask가 022일 경우:
        - 777 - 022 = 755 -> 생성되는 디렉터리의 권한은 755가 된다.
      - 또다른 예로, 디폴트 권한이 666인 파일에서 umask가 022일 경우:
        - 666 - 022 = 644 -> 생성되는 파일의 권한은 644가 된다.


# 특수 허가권

- 프로세스가 실행되는 동안 해당 파일을 실행한 사용자가 아닌, 해당 파일을 소유한 사용자의 권한으로 실행하도록 만드는 허가권.
- 기능
  - 낮은 수준의 사용자가 높은 수준의 자원에 접근 시 접근 제한으로 인해 발생하는 문제를 해결하기 위해 사용.
  - 프로세스를 실행하는 동안만 소유자나 그룹 권한으로 실행.
  - SetUID, SetGID 비트 : 소문자 s, 대문자 S, Sticky 비트 : 소문자 t, 대문자 T
    - 소문자 : 해당 파일에 실행 권한이 부여되어 있을 경우이며, 정상적인 권한으로 실행함.
      - ex: ```-rwsr-xr-x```(setUID, setGID), ```drwxrwxrwt```(Sticky Bit)
    - 대문자 : 해당 파일에 실행 권한이 부여되어 있지 않을 경우이며, 정상적인 권한으로 실행되진 않음. 
      - ex: ```-rwSr-xr-x```(setUID, setGID), ```drwxrwxrwT```(Sticky Bit)

이 특수 허가권은 일반적인 읽기, 쓰기, 실행 권한 외에 아래 세가지로 존재한다.

1. Setuid(SUID)
2. Setgid(SGID)
3. Sticky Bit

이 세 가지 각각에 대해 알아보기로 하자.

- Setuid (SUID)
  - 파일의 소유자 실행 권한에 UID 설정.
  - Setuid가 설정된 파일 실행시, 특정 작업 수행을 위해 일시적으로 파일 소유자의 권한을 부여하는 비트.
- Setgid (GID)
  - 파일의 그룹 실행 권한에 GID 설정.
  - Setgid가 설정된 파일 실행 시, 특정 작업 수행을 위해 일시적으로 파일 소유자 그룹의 권한을 부여하는 비트.
- Sticky Bit
  - 파일의 제3자 실행 권한에 Sticky Bit 설정.
  - Sticky Bit가 설정된 디렉터리 안의 파일에 모든 사용자에게 쓰기 권한이 부여되어 있을 경우에도 파일의 소유자나 root 사용자가 아니면 해당 파일을 삭제할 수 없음.
  - 누구나 파일을 생성, 수정은 가능

특수 허가권을 설정할 때 숫자(8진수) 모드를 사용할 수 있는데, 각 특수 허가권은 4자리의 8진수 표현을 통해 설정된다. 



또한, 기호 모드로도 사용할 수 있는데, 이를 아래 표를 통해 정리해보기로 한다.

- 특수 허가권 설정 방법

| 허가권 종류 | 기호 모드 | 숫자 모드 | 설명 |
| Setuid | chmod u+s filename | 4 | 실행 파일에 설정되어, 해당 파일이 소유자의 권한으로 실행됨 |
| Setgid | chmod g+s filename | 2 | 실행 파일이나 디렉터리에 설정되어, 해당 파일이 그룹 권한으로 실행됨. 디렉터리의 경우, 하위 파일이 부모 디렉터리의 그룹 소속으로 생성됨 |
| Sticky Bit | chmod +t directory | 1 | 디렉터리에 설정되어, 해당 디렉터리 내의 파일을 파일 소유자만 삭제할 수 있도록 제한함 |
| 일반 권한 | chmod u=rwx,g=rx,o=rx filename | 7,5,5 | 소유자, 그룹, 기타 사용자에 대한 읽기(r), 쓰기(w), 실행(x) 권한 설정 |

- 일반 권한 설정

| 권한 종류 | 기호 모드 | 숫자 모드 | 설명 |
| 읽기 | r | 4 | 파일을 읽을 수 있는 권한 |
| 쓰기 | w | 2 | 파일을 수정할 수 있는 권한 |
| 실행 | x | 1 | 파일을 실행할 수 있는 권한 |

- 특수 허가권과 일반 권한 결합 예시

| 전체 숫자 | 숫자 모드 |  기호 모드 | 설명 |
| 4755 | chmod 4755 filename | chmod u+s,g=rx,o=rx filename | SUID 설정, 소유자: rwx, 그룹: r-x, 기타: r-x |
| 2755 | chmod 2755 directory | chmod g+s,u=rwx,g=rx,o=rx directory	 | SGID 설정, 소유자: rwx, 그룹: r-x, 기타: r-x |
| 1777 | chmod 1777 /tmp | chmod +t,u=rwx,g=rwx,o=rwx /tmp | Sticky Bit 설정, 소유자: rwx, 그룹: rwx, 기타: rwx |
| 6755 | chmod 6755 filename | chmod u+s,g+s,u=rwx,g=rx,o=rx filename | SUID와 SGID 설정, 소유자: rwx, 그룹: r-x, 기타: r-x |
| 0700 | chmod 0700 filename | chmod u=rwx,g=,o= filename | 소유자만 모든 권한, 그룹 및 기타는 권한 없음 |


# 디스크 쿼터 (Disk Quota)

- 디스크 쿼터(Disk Quota)는 리눅스 또는 유닉스 시스템에서 사용자가 사용할 수 있는 디스크 공간과 파일 수를 제한하기 위해 설정하는 시스템 기능. 이를 통해 시스템 관리자들은 개별 사용자나 그룹이 사용할 수 있는 디스크 자원을 관리하고, 디스크 공간의 과도한 사용을 방지할 수 있음. 디스크 쿼터는 특히 다중 사용자 시스템이나 서버에서 매우 유용.
- 주요 개념
  - 1. 하드 제한 (Hard Limit)
    - 사용자가 절대 초과할 수 없는 디스크 공간 또는 파일 개수의 제한.
    - 사용자가 할당된 하드 제한을 넘으려 하면, 파일을 더이상 생성하거나 추가적인 디스크 공간 사용할 수 없음.
  - 2. 소프트 제한 (Soft Limit)
    - 사용자가 초과할 수 있는 임시적인 디스크 공간 또는 파일 개수의 제한.
    - 소프트 제한을 초과하면 경고가 발생하지만, 그레이스 기간(Grace Period) 동안은 디스크 공간을 계속 사용할 수 있음. 그레이스 기간이 지나면 소프트 제한도 하드 제한처럼 동작하여 추가 사용이 불가능해짐.
  - 3. 그레이스 기간 (Grace Period)
    - 사용자가 소프트 제한을 초과한 경우, 일정 기간 동안은 디스크 공간을 초과 사용하게 허용하는 기간. 그레이스 기간이 끝나면 소프트 제한을 넘지 못하게 됨.

- 디스크 쿼터 종류
  - 디스크 쿼터는 일반적으로 두가지 기준으로 설정할 수 있음.
    - 1. 디스크 사용량 제한 (Block Quota)
      - 사용자가 사용할 수 있는 디스크 공간의 양을 제한.
      - ex: 사용자에게 1GB의 공간을 할당하고, 이를 넘지 않도록 설정할 수 있음.
    - 2. 파일 개수 제한 (Inode Quota)
      - 사용자가 생성할 수 있는 파일 수 제한
      - ex: 한 사용자가 100,000개의 파일을 생성하는 것을 방지하기 위해 파일 수를 제한할 수 있음.

- 디스크 쿼터 설정 및 관리
  - 1. 쿼터 활성화
    - 파일 시스템에서 디스크 쿼터를 사용하려면 먼저 시스템에서 쿼터 기능을 활성화해야 함.
    - /etc/fstab 파일에서 특정 파일 시스템에 대해 쿼터 기능을 활성화할 수 있음.
      - ```/dev/sda1 /home ext4 defaults,usrquota,grpquota 0 2```
  - 2. 쿼터 설정 명령어
    - quotaon : 디스크 쿼터 기능을 활성화함.
      - ```root@noah-VirtualBox:~# quotaon [옵션] [사용자/그룹명]```
    - quotaoff : 디스크 쿼터 기능을 비활성화함.
      - ```root@noah-VirtualBox:~# quotaoff [옵션] [사용자/그룹명]```
    - quotacheck : 모든 파일 시스템을 점검하고, 쿼터 설정 및 기록 파일 갱신하는 명령어.
      - quota.user, quota.group 또는 aquota.user, aquota.group 파일을 점검하고 갱신.
      - ```root@noah-VirtualBox:~# quotacheck [옵션]```
    - edauota : 사용자의 디스크 쿼터를 설정하거나 수정할 수 있음.
      - ```root@noah-VirtualBox:~# edquota [옵션] [사용자/그룹명]```
    - setquota : 터미널에서 직접 사용자나 그룹에 쿼터를 적용하는 명령어.
      - ```root@noah-VirtualBox:~# setquota [옵션] [사용자/그룹명] [block soft limit] [block hard limit] [inode soft limit] [inode hard limit] [파티션명]```
    - repquota : 쿼터 상태를 보고함. 특정 사용자나 그룹이 사용한 디스크 공간 및 파일 수를 확인할 수 있음.\
      - ```root@noah-VirtualBox:~# repquota [옵션] [사용자/그룹명/파일 시스템명]```