---
title: 파일 시스템 관리 유틸리티
author: 노아
date: 2024-10-12 22:05:00 +0800
categories: [Linux, 파일 시스템 관리, 파일 시스템 관리 유틸리티]
tags: [리눅스, 파일 시스템 관리 유틸리티]
pin: true
math: true
mermaid: true

---
파일 시스템 관리
- 파일 시스템 관리 유틸리티

# 목차

- 파일 시스템 구조
- 파일 시스템 관련 명령어
- 파일 시스템 관련 파일

# 파일 시스템 구조

- 파일 시스템 구조 관련해서는 파일 시스템과 파티션에서 따로 정리를 했었다. 그러므로, 하단에 링크를 첨부하는 것으로 대체한다.
  - [페이지 참조](https://noah2byte.github.io/posts/file-system-partition1/)


# 파일 시스템 관련 명령어

- fdisk
  - 파티션을 생성, 수정, 제거 및 파일 시스템 유형을 지정하는 명령어4
  - 기본 형식
```
root@noah-VirtualBox:~# fdisk [옵션] [장치명]
```

- mkfs
  - 파일 시스템을 생성하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~# mkfs [옵션] [파일 시스템 유형] [장치명]
```

- mke2fs
  - mkfs 명령어의 확장 버전으로 파일 시스템을 생성하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~# mke2fs [옵션] [파일 시스템 유형] [블록 개수]
```

- mkfs.xfs
  - xfs 파일 시스템을 생성하는 명령어
  - 사용 방법

```
root@noah-VirtualBox:~# mkfs.xfs [옵션] [파티션명]
```

- fsck
  - 파일 시스템의 무결성 점검과 오류를 복구하는 명령어
  - lost+found 디렉터리에 저장된 파일을 복구하며, 복구가 완료되면 파일은 제거된다.
    - 참조 : lost+found 디렉터리는 파일 시스템이 손상되거나 비정상적으로 종료된 후, 파일 시스템 복구 도구(fsck)가 손실되거나 손상된 파일 조각들을 모아두는 곳.
  - 기본 형식

```
root@noah-VirtualBox:~# fsck [옵션] [장치명]
```

- e2fsck
  - fsck 명령어의 확장 버전
  - 파일 시스템의 무결성 점검과 오류를 복구하는 명령어
  - 기본 형식

```
root@noah-VirtualBox:~# e2fsck [옵션] [장치명]
```

- xfs_repair
  - xfs 파일 시스템을 검사 및 복구하는 명령어
  - 사용 방법

```
root@noah-VirtualBox:~# xfs_repair [옵션] [파티션명]
```

- mount, umount
  - 특정 장치와 디렉터리를 연결하는 명령어.
  - 기본적으로 주변 장치는 자동으로 마운트되지 않으므로, 시스템 부팅 후 수동으로 마운트하여 사용하고, 사용 완료 후에는 언마운트하여 연결을 종료해야 함.
  - 기본 형식

```
## mount
root@noah-VirtualBox:~# mount [옵션] [장치명] [마운트 포인트]

## umount
root@noah-VirtualBox:~# umount [마운트 포인트 또는 디바이스]

ex>
## -v 옵션 추가하여 출력 결과 확인
root@noah-VirtualBox:~# mount -f -v /dev/sda3 /data
mount: /dev/sda3 mounted on /data.
```

- eject
  - DVD나 CD-ROM 등의 미디어 장치를 해제하고, 꺼내는 명령어.
  - 기본 형식

```
root@noah-VirtualBox:~# eject [옵션] [장치명/마운트 포인트]
```

- df 
  - 시스템에 마운트된 하드디스크의 사용량과 남은 용량을 확인하는 명령어.
  - 기본적으로 블록 단위(1,024 바이트)로 출력함.
  - 기본 형식

```
root@noah-VirtualBox:~# df [옵션] [파일명]
```


# 파일 시스템 관련 파일

- /etc/fstab
  - 파일 시스템 관련 설정 정보를 저장하고 있는 파일.
  - 시스템 부팅 시 파일 시스템을 자동으로 마운트 하고자 할 때, 이 파일에 설정하면 됨.
  - 구조
    - /etc/fstab 파일의 각 행은 다섯 개의 필드로 구성되어 있음. 각 필드는 공백(탭)으로 구분됨.

```
# <file system> <mount point>   <type>  <options>       <dump>  <pass>
UUID=1234-5678  /               ext4    defaults        0       1
/dev/sda1       /mnt/data      xfs     defaults,noatime 0       0
/dev/sdb1       none           swap    sw              0       0
192.168.1.100:/export/share /mnt/nfs nfs defaults 0 0
```

| 필드 예시 | 필드 번호 | 필드 이름 | 설명 |
| /dev/sda1 | 1 | 파일 시스템 | 마운트할 장치의 장치 이름 (ex: /dev/sda1, UUID, LABEL 등) |
| /mnt/data | 2 | 마운트 포인트 | 파일 시스템이 마운트될 디렉터리 경로 (ex: /mnt/data) |
| xfs | 3 | 파일 시스템 타입 | 파일 시스템 타입 (ex: ext4, xfs, nfs, swap 등) |
| defaults,noatime | 4 | 옵션 | 마운트 옵션 (ex: defaults, ro, rw, noauto, user 등) |
| 0 | 5 | 덤프 유무 | 덤프 백업 유무를 나타내는 필드 (0 또는 1). 0은 덤프하지 않음을 의미 |
| 0 | 6 | 파일 시스템 체크 | 부팅 시 fsck 명령어에 의해 파일 시스템 체크 순서 지정 (0은 체크하지 않음). 1은 루트 파일 시스템, 2는 나머지 파일 시스템의 체크 순서 |


  - 옵션
    
| 옵션 | 설명 |
| defaults | 기본 옵션으로, rw, suid, dev, exec, auto, nouser, async가 포함됨 |
| ro | 읽기 전용으로 마운트 |
| rw | 읽기 및 쓰기 모드로 마운트 |
| noexec | 실행 파일을 실행할 수 없도록 함 |
| nosuid | set-user-identifier(UID) 비트 무시 |
| nodev | 장치 파일 허용하지 않음 |
| async | 비동기 모드로 데이터 저장 |
| sync | 모든 쓰기 작업이 완료된 후에 다음 작업을 진행 |
| auto | 부팅 시 자동으로 마운트 |
| noauto | 부팅 시 자동으로 마운트하지 않음 |
| user | 일반 사용자도 마운트할 수 있도록 허용 |
| nouser | 일반 사용자가 마운트할 수 없도록 함 |
| exec | 마운트된 파일 시스템에서 실행 파일을 실행할 수 있음 |
| noshare | NFS 공유 방지 |
| user_xattr | 사용자 정의 확장 속성 지원 |
| acl | ACL (Access Control Lists) 지원 |
| noatime | 파일 접근 시간 업데이트 하지 않음 |
| nodiratime | 디렉터리 접근 시간 업데이트 하지 않음 |
| quota | 디스크 쿼터 활성화 |
| usrquota | 사용자 기반 디스크 쿼터 활성화 |
| grpquota | 그룹 기반 디스크 쿼터 활성화 |

