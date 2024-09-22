---
title: 기본 명령어1
author: 노아
date: 2024-09-20 12:12:00 +0800
categories: [Linux, 기본 명령어, 기본 명령어1]
tags: [리눅스, 기본 명령어1]
pin: true
math: true
mermaid: true

---
기본 명령어1 
- 사용자 생성 및 계정 관리

# 목차

- 사용자 관련 명령어
- 사용자 관련 파일
- 사용자 계정 관리
- 사용자 정보 조회 명령어

# 서론

- 그러면 이제 리눅스 기본 명령어에 대해 정리하기로 한다. "기본 명령어" 포스팅에서 내가 자주 사용해왔고 현재도 사용중인 명령어들도 있을 테고, 모르고 있는 명령어들도 있을 것이다. 그러나 아는 명령어라고 하더라도 다시 한번 살펴보고 이번 기회에 정리하는 기회로 삼기로 한다. 또한 각 커멘드마다 존재하는 옵션의 경우에는 --help로 찾아보면 되니, 일일이 작성하지 않기로 한다. 마지막으로 이 포스팅에서 정리한 거 이외에도 많은 커멘드들이 있을 것으로 생각되나, 이에 대해서는 나중에 공부하면서 찾아본 연후에 다시 작성함을 원칙으로 한다.

# 사용자 관련 명령어

- useradd
  - 사용자 계정을 생성하는 명령어.
  - 생성된 사용자 계정 정보는 '/etc/passwd', '/etc/shadow', '/etc/group' 파일에 저장됨.
  - 기본 형식

```
root@noah-VirtualBox:~$ useradd [옵션] [계정명]

ex>
noah@noah-VirtualBox:~$ sudo useradd -c cindy girlfriend
[sudo] noah 암호:

확인>
noah@noah-VirtualBox:/home$ cat /etc/passwd
...
girlfriend:x:1001:1001:cindy:/home/girlfriend:/bin/sh
```

> <b>참조</b><br>
> <b>사용자</b>
> - 리눅스에서 '사용자'란, 시스템에 접근하고 작업을 수행할 수 있는 개별 계정을 가진 사람이나 프로세스를 의미.
> - 리눅스 시스템은 다중 사용자 운영체제로 설계되어 있어 여러 사용자가 동시에 시스템에 접속하고 자원을 공유할 수 있음.
> - 각 사용자는 고유한 사용자 이름(계정)과 함께 파일, 프로세스 및 시스템 자원에 대한 권한을 가짐.
> - 종류
>   - 루트 사용자(root)
>     - 시스템의 모든 권한을 가진 최상위 관리자 계정. 
>     - 시스템 설정을 변경하거나 다른 사용자의 파일을 관리 가능하며, 모든 작업 수행 가능.
>   - 일반 사용자
>     - 일반적으로 제한된 권한을 가진 사용자.
>     - 자기 자신과 관련된 파일 및 프로세스에만 접근할 수 있으며, 시스템의 주요 설정을 변경할 수 없음.
>   - 시스템 사용자
>     - 백그라운드에서 실행되는 시스템 프로세스나 데몬(ex: www-data, nobody 등)을 위해 생성된 사용자.
>     - 이들은 시스템 안정성과 보안을 위해 제한된 권한을 가지고 있음.
>   - 사용자는 id, whoami, users와 같은 명령어를 통해 현 사용자 정보 확인 가능.
>
>
> <b>/etc/group</b>
> - /etc/group 파일은 시스템의 그룹 정보를 저장함.
> - 리눅스에서는 사용자가 어떤 그룹에 속할 수 있으며, 파일이나 디렉터리의 권한 설정 등에 사용됨.
> - 구조 : /etc/group 파일도 콜론(:)으로 구분된 여러 필드로 이루어져 있음.
```
groupname:x:1000:user1,user2
```
>   - groupname : 그룹 이름
>   - x : 과거에는 그룹 비밀번호가 저장되었지만, 지금은 보통 X로 표시됨.
>   - GID(Group ID) : 그룹 식별 번호.
>   - 그룹 구성원 : 그룹에 속한 사용자들의 목록(콤마로 구분)

- passwd
  - 사용자 계정의 패스워드 변경 및 관리하는 명령어.
  - 생성된 패스워드 정보는 암호화되어 /etc/shadow 파일에 저장됨.
  - 기본 형식

```
[패스워드 변경]
root@noah-VirtualBox:/home$ passwd [계정명]

ex>
noah@noah-VirtualBox:/home$ passwd noah
noah에 대한 암호 변경 중
현재 비밀번호: 
새  암호: # 4자리로 입력
새  암호 재입력: 
더 긴 암호를 선택해 주십시오
새  암호: # 8자리로 입력함
새  암호 재입력: 
passwd: 암호를 성공적으로 업데이트했습니다

-----------------------

[패스워드 관리]
root@noah-VirtualBox:~$ passwd [옵션] [계정명ㅔ]

ex>
# girlfriend 계정 비밀번호 잠금
noah@noah-VirtualBox:~$ sudo passwd -l girlfriend
passwd: password expiry information changed.
-> girlfriend 계정으로 서버 로그인 안됨.

# girlfriend 계정 비밀번호 잠금 해제
noah@noah-VirtualBox:~$ sudo passwd -u girlfriend
[sudo] noah 암호: 
죄송합니다만, 다시 시도하십시오.
[sudo] noah 암호: 
passwd: password expiry information changed.
-> 잠금 해제 후 girlfriend 계정으로 재접속시 서버 로그인 됨
```

- su 
  - 'Switch User(또는 Substitute User)'의 약어로 현재 사용자 계정에서 로그아웃하지 않고, 다른 사용자로 전환하는 명령어.
  - 기본 형식

```
noah@noah-VirtualBox:~$ su [옵션] [사용자] [셸 변수]

ex>
noah@noah-VirtualBox:~$ su girlfriend
암호: 
$ 
```


# 사용자 관련 파일

- 1. /etc/default/useradd 파일
  - 사용자 계정 생성 시 가장 먼저 참조하는 파일.
  - vi 편집기 또는 useradd -D 명령어로 확인 및 변경 가능.
  - 파일 내용

```
# Default values for useradd(8)
#
# The SHELL variable specifies the default login shell on your
# system.
# Similar to DSHELL in adduser. However, we use "sh" here because
# useradd is a low level utility and should be as general
# as possible
SHELL=/bin/sh
#
# The default group for users
# 100=users on Debian systems
# Same as USERS_GID in adduser
# This argument is used when the -n flag is specified.
# The default behavior (when -n and -g are not specified) is to create a
# primary user group with the same name as the user being added to the
# system.
# GROUP=100
#
# The default home directory. Same as DHOME for adduser
# HOME=/home
#
# The number of days after a password expires until the account 
# is permanently disabled
# INACTIVE=-1
#
# The default expire date
# EXPIRE=
#
# The SKEL variable specifies the directory containing "skeletal" user
# files; in other words, files such as a sample .profile that will be
# copied to the new user's home directory when it is created.
# SKEL=/etc/skel
#
# Defines whether the mail spool should be created while
# creating the account
# CREATE_MAIL_SPOOL=yes
```

- 2. /etc/login.defs 파일
  - 새로 사용자 계정 생성 시 두 번째로 참조하는 파일로 기본값을 정의하는 파일.
  - 파일 내용

```
noah@noah-VirtualBox:~$ cat /etc/login.defs
#
# /etc/login.defs - Configuration control definitions for the login package.
#
# Three items must be defined:  MAIL_DIR, ENV_SUPATH, and ENV_PATH.
# If unspecified, some arbitrary (and possibly incorrect) value will
# be assumed.  All other items are optional - if not specified then
# the described action or option will be inhibited.
#
# Comment lines (lines beginning with "#") and blank lines are ignored.
#
# Modified for Linux.  --marekm

# REQUIRED for useradd/userdel/usermod
#   Directory where mailboxes reside, _or_ name of file, relative to the
#   home directory.  If you _do_ define MAIL_DIR and MAIL_FILE,
#   MAIL_DIR takes precedence.
...
(하단 생략)
```

- 3. /etc/skel 디렉터리
  - /etc/default/useradd 파일에서 SKEL 값은 /etc/skel 디렉터리를 의미.
  - useradd 명령을 사용하면 /etc/skel 디렉터리에 있는 파일들이 새롭게 생성되는 사용자의 홈 디렉터리로 복사됨.

```
noah@noah-VirtualBox:~$ cd /etc
noah@noah-VirtualBox:/etc$ cd skel
noah@noah-VirtualBox:/etc/skel$ ll
합계 28
drwxr-xr-x   2 root root  4096  3월 17  2023 ./
drwxr-xr-x 131 root root 12288  9월 22 13:51 ../
-rw-r--r--   1 root root   220  2월 25  2020 .bash_logout
-rw-r--r--   1 root root  3771  2월 25  2020 .bashrc
-rw-r--r--   1 root root   807  2월 25  2020 .profile
```

> 참조
> - .bash_logout : 사용자가 로그아웃할 때 실행되는 스크립트 파일. 이 파일은 사용자가 로그인 셸을 종료할 때 실행할 명령들을 정의하는데 사용됨.
>   - 주로 세션 정리 or 로그아웃 시 특정 작업을 수행하는데 사용됨.
>   - 예를 들어 화면 지우거나, 로그아웃 시 남겨진 임시 파일을 삭제하는 명령 등 포함.
>   - ex : ```clear```
> - .bash_profile : 사용자가 로그인 셸에 접속할 때 한 번 실행되는 스크립트. 로그인 셸은 사용자가 시스템에 로그인할 때 실행되는 셸을 의미(ex: ssh로 서버에 접속하거나 직접 콘솔에 로그인할 때)
>   - 로그인 시 사용자 환경을 설정하는데 사용됨.
>   - 환경변수, 별칭(alias), 셸 옵션 등을 설정하는 명령어가 여기에 포함됨.
>   - .bash_profile이 실행될 때 .bashrc 파일을 불러와 추가 설정을 적용하는 경우가 많음.
>   - ex : 
```
export PATH=$PATH:$HOME/bin
...
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi
```
>    - 리눅스나 유닉스 계열 시스템은 다른 로그인 셸 초기화 파일을 대신 사용하는 경우가 있으므로, .bash_profile 파일이 아닌, .profile이나 .bash_login 파일이 있을 수 있다. 만약, .bash_profile이 없다면 시스템은 .profile이나 .bash_login 파일을 찾아서 실행하려고 한다. 이는 .bash_profile, .bash_login, .profile이 모두 비슷한 역할을 하기 때문이며, 이 중 하나만 실행된다. 그리고 보통 .bash_profile이 있으면 이 파일이 우선 실행된다.
> - .bashrc : .bashrc 파일은 사용자가 비로그인 셸을 시작할 때 실행되는 스크립트이다. 비로그인 셸은 터미널 예물레이터에서 새로운 셸을 시작하거나 이미 로그인된 상태에서 추가로 실행되는 셸을 의미함(ex: 터미널에서 bash를 입력하여 새 셸을 실행하는 경우). 쉽게 말해서 터미널을 열 때마다 실행되는 설정 파일.
>   - 쉘에서 반복적으로 필요한 설정(ex: 별칭 설정, 프롬프트 설정 등)을 여기에 포함함.
>   - 일반적으로 비로그인 쉘에서 주로 사용되지만, .bash_profile에서 .bashrc를 불러와 로그인시에도 동일한 설정을 적용할 수 있음.<br>
>   -> 즉, 사용자가 터미널에서 일상적으로 자주 사용하는 명령어의 단축키, 환경 변수 설정 등을 자동으로 실행해주기 때문에 사용자의 터미널 경험을 최적화하고 반복 작업을 자동화하는데 매우 유용함.
>   - ex: ```alias ll='ls -la'```

- 4. /etc/passwd 파일
     - /etc/passwd 파일은 시스템의 사용자 계정 정보를 저장하는 텍스트 파일.
     - 이 파일은 모든 사용자에 의해 읽을 수 있지만, 쓰기 권한은 루트 사용자에게만 부여됨.
     - 구조 : 파일은 여러 줄로 이루어져 있으며, 각 줄은 하나의 사용자 정보를 나타냄. 각 줄은 콜론(:)으로 구분된 7개의 필드로 구성됨.
```
username:x:1000:1000:User Name:/home/username:/bin/bash
```
       - username : 사용자 이름
       - x : 비밀번호 필드. 과거에는 암호화된 비밀번호가 여기에 저장되었지만, 보안 강화를 위해 지금은 x로 표시되고 실제 비밀번호는 /etc/shadow 파일에 저장됨.
       - UID(User ID) : 사용자 식별 번호. 0은 root 사용자, 1000번부터는 일반 사용자.
       - GID(Group ID) : 사용자가 기본으로 속한 그룹의 식별 번호.
       - 사용자 정보 (GECOS) : 사용자에 대한 설명 (주로 사용자 이름)
       - 홈 디렉터리 : 사용자의 홈 디렉터리 경로.
       - 쉘 : 사용자가 로그인했을 때 사용할 기본 쉘.

- 5. /etc/shadow 파일
     - /etc/shadow 파일은 사용자 계정의 암호화된 비밀번호와 추가적인 보안 정보를 저장하는 파일.
     - 이 파일은 매우 민감하며, 루트 사용자만 접근 가능함.
     - 구조 : /etc/passwd와 비슷하게 각 줄이 콜론(:)으로 구분된 필드로 구성되어 있으며, 암호화된 비밀번호와 암호 관련 정보가 들어있음.
```
username:$6$hashed_password:18547:0:99999:7:::
```
      - username : 사용자 이름
      - 암호화된 비밀번호 : 암호화된 비밀번호가 저장됨. 비밀번호는 다양한 해시 알고리즘(SHA-512 등)을 사용하여 암호화됨.
        - $로 필드를 구분하며, 아래와 같이 구분함.
          - $algorithm_id$salt$encrpyted_password
            - algorithm_id -> 암호학적 해시 id로 자세한 설명은 아래와 같음.
              - 1 : MD5
              - 2 : Blow Fish
              - 5 : SHA-256
              - 6 : SHA-512
            - salt : 각 해시에 첨가할 랜덤값으로, 해당 값에 따라 해시 값이 바뀜.
            - encrpyted_password : 알고리즘과 salt로 패스워드를 암호화한 값.
        - * : 
          - 계정이 비밀번호를 전혀 사용하지 않음을 나타냄.
          - *가 비밀번호 필드에 있으면, 해당 계정은 비밀번호가 없는 계정이며, 비밀번호로는 로그인할 수 없음.
          - * 문자가 있는 계정은 일반적으로 비밀번호에 로그인하는 것이 아니라, 시스템 서비스 계정(ex: ftp, www-data 등)이나 다른 인증 방식(ex: SSH 키)을 사용하는 경우가 많음.
        - ! : 
          - 계정 잠금을 의미. 
          - !가 암호화된 비밀번호 앞에 있으면, 해당 계정은 비밀번호를 사용한 인증을 할 수 없음. 
          - 계정의 잠금을 해제하려면 관리자가 암호화된 비밀번호에서 !를 제거하거나 새 비밀번호를 설정해야 함.
      - 최종 비밀번호 변경일 : 비밀번호가 마지막으로 변경된 날짜(기준일은 1970년 1월 1일).
      - 비밀번호 최소 사용 기간 : 비밀번호를 변경할 수 없는 최소 일수.
      - 비밀번호 최대 사용 기간 : 비밀번호를 사용 가능한 최대 일수.
      - 비밀번호 경고 기간 : 비밀번호 만료 전에 사용자에게 경고하는 기간.
      - 비밀번호 비활성 기간 : 비밀번호 만료 후 계정이 비활성화되는 기간.
      - 계정 만료일 : 계정이 만료되는 날짜.


# 사용자 계정 관리

- usermod
  - 사용자 계정 정보를 변경하는 명령어.
  - 사용자의 계정 명, UID, GID, 홈 디렉터리 등을 변경하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ usermod -d [옵션] [설정값] [계정명]

ex>
noah@noah-VirtualBox:~$ sudo usermod -d /home/cindy girlfriend
[sudo] noah 암호: 
죄송합니다만, 다시 시도하십시오.
[sudo] noah 암호: 

확인>
noah@noah-VirtualBox:/home$ getent passwd girlfriend
girlfriend:x:1001:1001:cindy:/home/cindy:/bin/sh
```

- userdel
  - 사용자 계정 정보를 삭제하는 명령어.
  - 옵션 지정 없이 해당 명령어를 실행하면, /etc/passwd, /etc/shadow, /etc/group 파일의 사용자 계정 정보가 삭제된다.
  - 기본 형식

```
root@noah-VirtualBox:/home$ userdel [옵션] [계정명]
```


# 사용자 정보 조회 명령어

- users
  - 시스템에 로그인한 사용자의 정보를 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:/home$ users

ex>
noah@noah-VirtualBox:/home$ users
noah noah
```

- w
  - 시스템에 로그인한 사용자의 정보를 자세히 출력하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:/home$ w

ex>
noah@noah-VirtualBox:/home$ w
 16:34:13 up 27 min,  2 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
noah     :0       :0               16:07   ?xdm?  17.16s  0.00s /usr/lib/gdm3/gdm-x-session --run-script env GNOME_SHELL_SESSION_MODE=ubuntu /usr/bin/gnome-session --systemd --session=ubuntu
noah     pts/0    10.0.2.2         16:07    1.00s  0.06s  0.00s w
```

   - TTY : 사용자가 연결된 터미널 장치. tty1, pts/0 등으로 나타나며, 물리적 터미널(콘솔) 또는 가상 터미널을 의미.
     - tty : 로컬 시스템 콘솔의 가상 터미널.
     - pts : 원격 터미널.
   - FROM : 사용자가 로그인한 원격지 주소 또는 호스트명. 원격지에서 로그인한 경우 IP 주소나 호스트명이 표시되며, 로컬 로그인일 경우 :0처럼 표시될 수 있음.
   - LOGIN@ : 사용자가 로그인한 시간을 나타냄.
   - IDLE : 사용자가 아무런 활동을 하지 않은 시간. 사용자가 활동 중이면 값이 0으로 나타남.
   - JCPU : 사용자가 사용하는 모든 프로세스에 의해 소비된 CPU 시간. 예를 들어, 여러 프로그램이 동시에 실행 중이면 모두 합산된 CPU 사용 시간이 나타남.
   - PCPU : 현재 사용자가 실행 중인 활성 프로세스에 의한 CPU 사용 시간.
   - WHAT : 사용자가 현재 실행 중인 명령어 또는 프로그램. 예를 들어, bash, vim, python 같은 명령이 이 필드에 표시됨.

- who
  - 시스템에 로그인한 사용자의 정보를 간단히 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ who [옵션]

ex>
noah@noah-VirtualBox:~$ who
noah     :0           2024-09-22 16:07 (:0)
noah     pts/0        2024-09-22 16:07 ...
```

- whoami
  - 시스템에 로그인한 사용자를 출력하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~$ whoami

ex>
noah@noah-VirtualBox:~$ whoami
noah
```

- id
  - 시스템에 로그인한 사용자의 UID, GID, GROUP 정보를 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ id

noah@noah-VirtualBox:~$ id
uid=~(~) gid=~(~) 그룹들=~(~),1(~),2(~),3(~),4(~),5(~),6(~),7(~),8(~)~
```