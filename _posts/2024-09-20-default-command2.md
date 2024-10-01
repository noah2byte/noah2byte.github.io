---
title: 기본 명령어2
author: 노아
date: 2024-09-20 12:12:00 +0800
categories: [Linux, 기본 명령어, 기본 명령어2]
tags: [리눅스, 기본 명령어2]
pin: true
math: true
mermaid: true

---
기본 명령어2
- 그룹 생성 및 그룹 관리

# 목차

- 그룹 관리 명령어
- 그룹 관련 파일
- 그룹 정보 조회 명령어

# 그룹 관리 명령어
- groupadd
  - 그룹 생성 시 사용하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ groupadd [옵션] [그룹명]

ex> 
noah@noah-VirtualBox:~$ tail -2 /etc/group
sambashare:x:134:noah
systemd-coredump:x:999:

##groupadd -g (GID) 그룹명
noah@noah-VirtualBox:~$ sudo groupadd -g 1004 test2
[sudo] noah 암호: 

noah@noah-VirtualBox:~$ tail -2 /etc/group
systemd-coredump:x:999:
test2:x:1004:
```

- groupdel
  - 그룹 삭제시 사용하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~$ groupdel [그룹명]

ex>
noah@noah-VirtualBox:~$ sudo groupdel test2
noah@noah-VirtualBox:~$ tail -2 /etc/group
sambashare:x:134:noah
systemd-coredump:x:999:
noah@noah-VirtualBox:~$ 
```

- groupmod
  - 그룹 정보 변경 시 사용하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~$ sudo groupmod [옵션] [그룹명]

ex>
noah@noah-VirtualBox:~$ tail -2 /etc/group
test2:x:1004:
test3:x:1005:

noah@noah-VirtualBox:~$ sudo groupmod -n noah2 test2
noah@noah-VirtualBox:~$ tail -2 /etc/group
test3:x:1005:
noah2:x:1004:
```


# 그룹 관련 파일
- /etc/group 파일
  - 사용자 그룹 정보가 저장되어 있는 파일.
  - 4개의 필드로 구성되어 있으며 그룹명, GID, 소속된 사용자 등을 저장함.
  - 파일 구조
    - groupname:password:gid:members
      - groupname -> 그룹명
      - password -> 패스워드
      - gid -> GID
      - members -> 소속된 사용자

- /etc/gpasswd 파일
  - 그룹의 패스워드가 암호화되어 저장되어 있는 파일.
  - 4개의 필드로 구성되어 있으며 그룹명, 패스워드 등을 저장.
  - 파일 구조
    - groupname:password:owner:members
      - groupname -> 그룹명
      - password -> 패스워드
      - owner -> 소유주
      - members -> 소속된 사용자


# 그룹 정보 조회 명령어
- groups
  - 현재 사용자가 속한 그룹 정보를 확인하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ groups

ex>
## noah라는 사용자가 noah adm ... 등등의 그룹에 소속되어 있는 것 확인
noah@noah-VirtualBox:~$ groups
noah adm cdrom sudo dip plugdev lpadmin lxd sambashare
```
