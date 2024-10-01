---
title: 기본 명령어3
author: 노아
date: 2024-09-20 12:12:00 +0800
categories: [Linux, 기본 명령어, 기본 명령어3]
tags: [리눅스, 기본 명령어3]
pin: true
math: true
mermaid: true

---
기본 명령어3
- 디렉터리 및 파일

# 목차

- 디렉터리 관련 명령어
- 파일 관련 명령어
- 파일 내용 출력 명령어
- 파일 내용 비교 명령어
- 리다이렉션과 파이프

# 디렉터리 관련 명령어
- mkdir
  - 디렉터리 생성하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~$ mkdir [옵션] [디렉터리명]

ex>
noah@noah-VirtualBox:~$ mkdir -p noah-test/hest
noah@noah-VirtualBox:~$ cd noah-test/
noah@noah-VirtualBox:~/noah-test$ ls
hest
```

- rmdir
  - 디렉터리 삭제 시 사용하는 명령어
  - 빈 디렉터리만 가능하며, 해당 디렉터리에 파일이나 디렉터리가 존재하면 삭제할 수 없다.
  - 기본 형식

```
root@noah-VirtualBox:~$ rmdir [디렉터리명]

ex>
noah@noah-VirtualBox:~$ rmdir noah-test/
rmdir: failed to remove 'noah-test/': 디렉터리가 비어있지 않음
noah@noah-VirtualBox:~$ cd noah-test/
noah@noah-VirtualBox:~/noah-test$ rmdir hest
noah@noah-VirtualBox:~/noah-test$ ll
합계 8
drwxrwxr-x  2 noah noah 4096 10월  1 12:53 ./
drwxr-xr-x 16 noah noah 4096 10월  1 12:51 ../
noah@noah-VirtualBox:~/noah-test$ 
```

- cd
  - 디렉터리 이동 시 사용하는 명령어.
  - 디렉터리는 절대 경로와 상대 경로로 지정할 수 있음.
  - 기본 형식

```
root@noah-VirtualBox:~/noah-test$ cd [대상 디렉터리]

ex>
noah@noah-VirtualBox:~/noah-test$ cd ~
noah@noah-VirtualBox:~$ pwd
/home/noah
noah@noah-VirtualBox:~$ 
```

- pwd
  - 현재 작업 중인 디렉터리를 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ pwd [옵션]

ex>
noah@noah-VirtualBox:~$ pwd
/home/noah
```


# 파일 관련 명령어
- ls
  - 디렉터리 안의 파일이나 디렉터리 목록을 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/noah-test$ ls [옵션] [디렉터리명]

ex>
noah@noah-VirtualBox:~/noah-test$ ls
test2.sh  test22  test3  test33
```

- cp
  - 파일이나 디렉터리를 복사하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ cp [옵션] [원본 파일/디렉터리] [대상 디렉터리]

ex>
noah@noah-VirtualBox:~/cptest$ cp ./test.sh ./test2.sh
noah@noah-VirtualBox:~/cptest$ cat test.sh
atest
noah@noah-VirtualBox:~/cptest$ cat test2.sh 
atest
```

- mv
  - 파일이나 디렉터리 이동 시 사용하는 명령어.
  - 파일이나 디렉터리 이름 변경 시 사용하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ mv [옵션] [원본 파일/디렉터리] [대상 파일/디렉터리]

ex>
noah@noah-VirtualBox:~/cptest$ ll
합계 20
drwxrwxr-x  3 noah noah 4096 10월  1 13:23 ./
drwxr-xr-x 17 noah noah 4096 10월  1 13:20 ../
-rw-rw-r--  1 noah noah    6 10월  1 13:20 test.sh
-rw-rw-r--  1 noah noah    6 10월  1 13:21 test2.sh
drwxrwxr-x  2 noah noah 4096 10월  1 13:23 testtest/
noah@noah-VirtualBox:~/cptest$ mv test2.sh ./testtest/
noah@noah-VirtualBox:~/cptest$ ll
합계 16
drwxrwxr-x  3 noah noah 4096 10월  1 13:23 ./
drwxr-xr-x 17 noah noah 4096 10월  1 13:20 ../
-rw-rw-r--  1 noah noah    6 10월  1 13:20 test.sh
drwxrwxr-x  2 noah noah 4096 10월  1 13:23 testtest/
noah@noah-VirtualBox:~/cptest$ cd testtest
noah@noah-VirtualBox:~/cptest/testtest$ ll
합계 12
drwxrwxr-x 2 noah noah 4096 10월  1 13:23 ./
drwxrwxr-x 3 noah noah 4096 10월  1 13:23 ../
-rw-rw-r-- 1 noah noah    6 10월  1 13:21 test2.sh
```

- rm
  - 파일이나 디렉터리 삭제 시 사용하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ rm [옵션] [파일/디렉터리명]

ex>
drwxrwxr-x  3 noah noah 4096 10월  1 13:23 ./
drwxr-xr-x 17 noah noah 4096 10월  1 13:20 ../
-rw-rw-r--  1 noah noah    6 10월  1 13:20 test.sh
drwxrwxr-x  2 noah noah 4096 10월  1 13:23 testtest/
noah@noah-VirtualBox:~/cptest$ rm -rf testtest
noah@noah-VirtualBox:~/cptest$ ll
합계 12
drwxrwxr-x  2 noah noah 4096 10월  1 13:25 ./
drwxr-xr-x 17 noah noah 4096 10월  1 13:20 ../
-rw-rw-r--  1 noah noah    6 10월  1 13:20 test.sh
```

- touch
  - 파일 크기가 0바이트인 빈 파일을 생성하는 명령어.
  - 현재 시간으로 파일의 접근 시간, 수정 시간 변경 시간 등의 타임 스탬프를 변경하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ touch [옵션] [설정값] [파일/디렉터리명]

ex>
noah@noah-VirtualBox:~/cptest$ touch -t 199912252359 testtesttest.sh
noah@noah-VirtualBox:~/cptest$ 
noah@noah-VirtualBox:~/cptest$ 
noah@noah-VirtualBox:~/cptest$ ll
합계 12
drwxrwxr-x  2 noah noah 4096 10월  1 13:30 ./
drwxr-xr-x 17 noah noah 4096 10월  1 13:20 ../
-rw-rw-r--  1 noah noah    6 10월  1 13:20 test.sh
-rw-rw-r--  1 noah noah    0 10월  1 13:28 testtest.sh
-rw-rw-r--  1 noah noah    0 12월 25  1999 testtesttest.sh
```

- file
  - 파일의 유형 및 속성 확인 시 사용하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ file [옵션] [파일/디렉터리명]

ex>
noah@noah-VirtualBox:~/cptest$ file test.sh
test.sh: ASCII text
```

- find
  - 리눅스와 유닉스 계열 시스템에서 파일과 디렉터리 검색하는 강력한 도구.
  - 파일 이름, 유형, 크기, 수정 시간 등 다양한 조건을 기준으로 검색 가능하며, 검색 결과에 대해 추가적인 작업(삭제, 복사 등)을 자동으로 수행할 수도 있음.
  - 기본 형식

```
root@noah-VirtualBox:~$ find [경로] [검색 조건] [후속 작업]
``` 

  - 주요 옵션 및 사용 예시
    - 1. 이름으로 검색
        - ```-name``` 옵션을 사용하여 파일 이름을 기준으로 검색할 수 있음.
        - ```find /home/user -name "*.txt"```
            - 이 명령어는 /home/user 경로에서 .txt 확장자로 끝나는 모든 파일을 검색함.
    - 2. 타입으로 검색
        - ```-type``` 옵션은 파일 유형을 기준으로 검색. 일반 파일, 디렉터리, 심볼릭 링크 등을 지정할 수 있음.
        - f : 일반 파일
        - d : 디렉터리
        - l : 심볼릭 링크
        - ```find /var/log -type f``` 혹은 ```find /var -type d```
    - 3. 파일 크기로 검색
        - ```-size``` 옵션을 사용하여 파일 크기를 기준으로 검색.
        - + : 지정한 크기보다 큰 파일
        - - : 지정한 크기보다 작은 파일
        - c : 바이트 기준
        - k : 킬로 바이트 기준
        - M : 메가 바이트 기준
        - ```find /home/user -size +10M``` 혹은 ```find /var/log -size -100k```
    - 4. 수정 시간으로 검색
        - ```-mtime```, ```-atime```, ```-ctime``` 옵션을 사용하여 파일의 수정, 접근, 생성 시간을 기준으로 검색할 수 있음.
        - -mtime: 파일 수정 시간
        - -atime: 파일 접근 시간
        - -ctime: 파일 생성(또는 메타데이터 변경 시간)
        - ```find /tmp -mtime -7``` 혹은 ```find /home/user -atime +30```
    - 5. 권한으로 검색
        - ```-perm``` 옵션을 사용하여 파일의 권한을 기준으로 검색할 수 있음.
        - ```find /etc -perm 644``` 혹은 ```find /var/www -perm /u+x```
        - /u=r와 같은 표시는 find 명령어에서 '파일 권한'을 나타낼 때 사용되는 형식. 이 형식은 -perm 옵션과 함께 사용되며, 파일의 읽기, 쓰기, 실행 권한을 기준으로 검색할 때 유용함. 또한, 여기서 /는 OR 조건을 의미하며, 여러 권한 조건 중 하나라도 만족하면 검색 결과에 포함시킨다는 의미.
    - 6. 소유자로 검색
        - ```-user```, ```-group``` 옵션을 사용하여 파일 소유자 또는 그룹을 기준으로 검색할 수 있음.
        - ```find /home -user alice``` 혹은 ```find /srv -group admin```
    - 7. 결과에 대해 작업 수행
        - ```-exec``` 옵션을 사용하면 검색된 파일에 대해 특정 명령어를 실행할 수 있음. 명령어 끝에 {}는 검색된 파일의 이름이 들어가는 위치를 나타내며, \;는 명령어의 종료를 의미함.
        - ```find /var/log -name "*.log" -exec rm {} \;``` 혹은 ```find /home/user -type f -exec chmod 644 {} \;```
    - 8. 결과 삭제
        - ```-delete``` 옵션을 사용하여 검색된 파일을 즉시 삭제할 수 있음.
        - ```find /tmp -name "*.tmp" -delete```
    - 9. 심볼릭 링크 무시
        - 심볼릭 링크를 무시하고 실제 파일만 검색하려면 -P 옵션을 사용한다.
        - ```find /home -P -name "*.sh"```

  - 검색 결과의 논리적 결합
    - AND 연산 (기본값) : 두 개 이상의 조건을 동시에 만족하는 파일을 찾는다.
      - ```find /var/log -type f -name "*.log"```
    - OR 연산(-o) : 두 조건 중 하나라도 만족하는 파일을 찾는다.
      - ```find /home/user -name "*.txt" -O -name "*.pdf"```
    - NOT 연산(!) : 특정 조건을 만족하지 않는 파일을 찾는다.
      - ```find /home/user ! -name "*.txt"```

- locate
  - 파일의 위치를 검색하는 명령어.
  - 미리 만들어 놓은 DB 파일에서 파일을 검색하기 때문에 빠른 검색이 가능하지만 DB 파일을 업데이트하지 않으면 최근에 삭제된 파일도 검색이 되는 문제가 발생할 수 있음. 이런 문제를 해결하려면 locate 명령어를 사용하기 전에 updatedb 명령을 실행하는 것이 좋음.
  - 기본 형식

```
root@noah-VirtualBox:~$ locate [옵션] [파일명]

ex>
noah@noah-VirtualBox:~$ locate cptest
/home/noah/cptest
/home/noah/cptest/test.sh
/home/noah/cptest/testtest.sh
/home/noah/cptest/testtesttest.sh
```

- whereis
  - 명령어의 바이너리(실행 파일), 소스, 매뉴얼 파일의 위치를 검색하는 명령어.
  - 기본 형식

```
noah@noah-VirtualBox:~$ whereis [검색할 명령어]

ex>
noah@noah-VirtualBox:~$ whereis cp
cp: /usr/bin/cp /usr/share/man/man1/cp.1.gz
```

- which
  - 명령어 실행 파일(또는 링크)의 위치를 검색하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~$ which [검색할 명령어]

ex>
noah@noah-VirtualBox:~$ which ls
/usr/bin/ls
```


# 파일 내용 출력 명령어
- cat 
  - 파일 내용을 출력하거나 두 개의 파일 내용을 합치는 명령어
  - 기본 형식

```
noah@noah-VirtualBox:~$ cat [옵션] [파일명]

ex>
noah@noah-VirtualBox:~$ cat cptest/test.sh
atest
noah@noah-VirtualBox:~$ cat -n cptest/test.sh
     1	atest
```

- head
  - 파일의 처음 행부터 지정한 줄 수만큼 출력하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~$ head [옵션] [설정값] [파일명]

ex>
noah@noah-VirtualBox:~$ head -1 cptest/test.sh
atest
```

- tail
  - 파일의 마지막 행부터 지정한 줄 수만큼 출력하는 명령어
  - 기본 형식

```
noah@noah-VirtualBox:~$ tail [옵션] [설정값] [파일명]

ex>
noah@noah-VirtualBox:~$ tail -1 cptest/test.sh
atest
```

- more
  - 파일의 내용을 한 화면에 표시할 수 있는 만큼 출력한 후, 사용자가 Enter 키나 Space 키를 눌러 다음 부분을 볼 수 있도록 해줌.
  - 제약 :
    - 뒤로 이동할 수 없음 : more는 기본적으로 파일을 앞으로만 스크롤함. 즉, 한 번 넘긴 내용을 다시 뒤로 갈 수 없음.
    - 기능 제한 : 파일의 내용을 단순히 한 화면씩 넘기기 위한 목적으로 만들어졌기 때문에, 추가적인 탐색 기능이 부족함.
  - 기본 형태

```
root@noah-VirtualBox:~$ more [파일명]

ex>
noah@noah-VirtualBox:~$ more /etc/passwd
root:x:0:0:root:/root:/bin/bash
...
```

- less
  - less 명령어는 more 명령어와 비슷하지만, 더 많은 기능 제공함. 파일 내용을 위아래로 자유롭게 스크롤할 수 있으며, 검색 기능 등 다양한 탐색 옵션을 지원함.
  - 장점 : 
    - 뒤로 이동 가능 : less는 파일 내용을 앞으로만 이동할 수 있는 more와 달리, 앞뒤로 자유롭게 스크롤 가능.
    - 파일 전체를 읽지 않음 : less는 파일의 내용 전체를 한 번에 읽어들이지 않고, 필요할 때마다 읽는다. 따라서 큰 파일도 빠르게 열 수 있음.
    - 추가적인 탐색 가능 : 여러 줄 이동, 특정 행으로 바로 이동, 특정 텍스트 검색 등이 가능함.
  - 기본 형식

```
root@noah-VirtualBox:~$ less [파일명]

ex>
noah@noah-VirtualBox:~$ less /etc/passwd

~

root:x:0:0:root:/root:/bin/bash
...
/etc/passwd (END)
```

- grep
  - 파일 안에서 지정한 패턴이나 문자열을 검색한 후 그 패턴을 포함하고 있는 모든 행을 표준 출력한다.
  - 한 디렉터리 안에서 지정한 패턴을 포함하는 파일을 출력할 수도 있음.
  - 종류 :
    - grep : 다중 패턴 검색
    - egrep : 정규 표현식 검색
    - fgrep : 단순 패턴 검색
  - 기본 형식 :

```
root@noah-VirtualBox:~$ grep [문자열] [옵션] [파일명]

ex>
noah@noah-VirtualBox:~$ grep -n t cptest/test.sh
1:atest
```

- wc
  - 파일 안의 행, 단어, 문자수를 출력하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~$ wc [옵션] [파일명]

ex>
noah@noah-VirtualBox:~$ wc cptest/test.sh
1 1 6 cptest/test.sh
```

- sort
  - 명령어 수행 결과나 파일 내용을 정렬하여 출력하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ [옵션] [파일명]

ex>
noah@noah-VirtualBox:~/cptest$ cat test4.sh
dlfdjflnm
dfdfdf

b vbfgdfgdf

vfdfevbbsvx


erefdfdd
noah@noah-VirtualBox:~/cptest$ 
noah@noah-VirtualBox:~/cptest$ 
noah@noah-VirtualBox:~/cptest$ 
noah@noah-VirtualBox:~/cptest$ sort test4.sh




b vbfgdfgdf
dfdfdf
dlfdjflnm
erefdfdd
vfdfevbbsvx
```

- cut 
  - 파일에서 특정 필드를 추출하여 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ cut [옵션] [파일명]

ex>
noah@noah-VirtualBox:~/cptest$ cat test5.sh
abc def efg

Aa dddfd  dfdf
dd
noah@noah-VirtualBox:~/cptest$ cut -c 1-2 test5.sh
ab

Aa
dd

```

- split
  - 하나의 파일을 여러 개의 파일로 분할하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ split [옵션] [파일명]

ex>
noah@noah-VirtualBox:~/cptest$ split -b 20 test5.sh
noah@noah-VirtualBox:~/cptest$ ll
합계 28
drwxrwxr-x  2 noah noah 4096 10월  1 15:17 ./
drwxr-xr-x 17 noah noah 4096 10월  1 13:20 ../
..
-rw-rw-r--  1 noah noah   31 10월  1 15:15 test5.sh
..
-rw-rw-r--  1 noah noah   20 10월  1 15:17 xaa
-rw-rw-r-  1 noah noah   11 10월  1 15:17 xab

```


# 파일 내용 비교 명령어
- diff
  - 두 개의 파일을 비교하여 다른 내용을 출력하는 명령어.
  - 실행 결과 차이점은 없다면 0, 차이점이 있자면 1, 에러 상황이라면 2 이상의 값을 반환한다.
  - diff3 명령어는 파일을 3개까지 비교하여 차이점을 출력함.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ diff [옵션] [파일1] [파일2]

ex>
noah@noah-VirtualBox:~/cptest$ diff test.sh test4.sh
1c1,9
< atest
---
> dlfdjflnm
> dfdfdf
> 
> b vbfgdfgdf
> 
> vfdfevbbsvx
> 
> 
> erefdfdd
```

- cmp
  - 두 파일을 바이트 단위로 비교하여 출력하는 명령어
  - 기본 형식

```
noah@noah-VirtualBox:~/cptest$ cmp [옵션] [파일1] [파일2]

ex>
noah@noah-VirtualBox:~/cptest$ cmp test.sh test4.sh
test.sh test4.sh differ: byte 1, line 1
```

- comm
  - 두 파일을 행 단위로 비교하여 차이점을 출력하는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~/cptest$ comm [옵션] [파일1] [파일2]

ex>
noah@noah-VirtualBox:~/cptest$ comm -1 test.sh test4.sh
dlfdjflnm
comm: file 2 is not in sorted order
dfdfdf

b vbfgdfgdf

vfdfevbbsvx


erefdfdd
```


# 리다이렉션과 파이프
- 리다이렉션(Redirection)
  - 표준 입력과 출력을 재지정하는 기능.
  - 표준 입력, 출력과 오류를 화면이나 파일로 출력되도록 재지정함.
  - 표준 입력장치는 키보드, 표준 출력 장치는 모니터.
  - 옵션
    - ```>``` : 
      - 명령을 화면에 출력하는 것이 아니라 프린터나 파일로 출력하도록 지정.
      - 지정한 파일이 존재하면 덮어쓰고, 존재하지 않으면 새로운 파일을 생성.
    - ```>>``` : 지정한 파일이 존재하면 명령 실행 결과를 파일에 추가하고, 존재하지 않으면 새로운 파일을 생성.
    - ```<``` : 키보드가 아닌 지정된 파일에서 입력 내용을 읽어옴.
    - ```>&``` : 명령의 출력을 다른 명령의 입력으로 보냄.
    - ```<&``` : 명령의 입력을 읽고, 다른 명령의 출력으로 보냄.
  - 기본 형식

```
noah@noah-VirtualBox:~/cptest$ cat [파일1] > [파일2]

ex>
noah@noah-VirtualBox:~/cptest$ cat test4.sh > test.sh
noah@noah-VirtualBox:~/cptest$ cat test.sh
dlfdjflnm
dfdfdf

b vbfgdfgdf

vfdfevbbsvx


erefdfdd
```

- 파이프(Pipe)
  - 두 개의 명령어를 연결하는 기능. 즉 프로세스와 프로세스 간의 통로라 할 수 있음.
  - 명령 출력이 다른 명령의 입력으로 전달된다.
  - 명령어와 명령어의 연결은 | 기호를 사용함.
  - 기본 형식
    - ```root@noah-VirtualBox:~$ [명령어1] | [명령어2] | [명령어3]```
  - 활용
    - ```ps aux | grep httpd```

- 세미콜론(;)
  - 하나의 명령어 라인에 여러 개의 명령을 실행할 수 있도록 도와준다.
  - 첫 번째 명령이 실패하여도 다음 명령을 실행함.
  - 기본 형식
    - ```root@noah-VirtualBox:~$ [명령어1] ; [명령어2] ; [명령어3]```
  - 활용
    - ```make ; make modules ; make modules_install ; make install```