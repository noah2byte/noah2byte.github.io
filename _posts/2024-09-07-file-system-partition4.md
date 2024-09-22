---
title: 파일 시스템과 파티션4
author: 노아
date: 2024-09-07 20:07:00 +0800
categories: [Linux, 파일 시스템과 파티션, 파일 시스템과 파티션4]
tags: [리눅스, 파일 시스템, 파티션4]
pin: true
math: true
mermaid: true

---
파일 시스템과 파티션4

# 목차

- RAID(Redundant Array of Independent Disks)

# RAID(Redundant Array of Independent Disks)

- RAID는 아래와 같이 정리할 수 있다.
  - 여러 개의 물리적인 하드디스크를 하나의 논리적인 디스크로 인식하게 만드는 기술이다.
  - 중요한 데이터를 가지고 있는 서버에 주로 사용되며 여러 개의 하드디스크에 동일한 데이터를 다른 위치에 중복해서 저장하는 기술이다.
  - 데이터를 저장하는 방법에 따라 다양한 방법이 있으며 이 방법들을 레벨이라 한다. 레벨에 따라 성능을 향상하거나, 저장장치의 신뢰성을 높이는데 사용한다.
- 종류
  - 하드웨어 RAID
    - RAID 기능을 하드웨어로 구현한 것
    - 하드웨어 제조업체에서 여러 개의 하드디스크로 만들어 공급
    - 안정적이지만 고가
  - 소프트웨어 RAID
    - RAID 기능을 소프트웨어로 구현한 것
    - 주로 운영체제 안에서 구현되며, 하드웨어 RAID 대안
    - 하드웨어 구성에 비해 성능 향상 적고, 안정성 떨어짐

- RAID 레벨 구조
  - RAID 0
    - 빠른 데이터의 입출력을 위해 스트라이핑(Striping) 사용
    - 하나의 디스크에 오류가 발생하면 모든 데이터를 잃어버릴 수 있음
    - * 스트라이핑(Striping) : 성능 향상을 위해 데이터를 1개 이상의 디스크 드라이브에 저장하여 드라이브를 병렬로 사용할 수 있는 기술. 즉, 논리적으로 연속된 데이터들이 여러 개의 물리적인 디스크 드라이브에 나누어 저장하는 기술.

    ![Desktop View](/assets/img/linux/file/raid/raid0.png){: width="972" height="589"}
    (사진 출처 : https://medium.com/@PITSGlobalDataRecoveryServices/raid-0-explained-d8edb9be5a9e)

  - RAID 1
    - 두 개 이상의 디스크를 미러링(Mirroring)을 통해 하나의 디스크처럼 사용
    - 완전히 동일하게 데이터를 복제하기 때문에 사용할 수 있는 용량이 절반 밖에 되지 않음
    - 하나의 디스크에 오류가 발생하면 미러링된 디스크를 통해 복구 가능
    - * 미러링(Mirroring)
      - 같은 데이터를 2개의 디스크에 저장하여 복사본을 만드는 기술
      - 1개의 디스크에 고장이 발생해도 다른 디스크의 데이터는 손상되지 않아 데이터를 보호할 수 있는 기술

          ![Desktop View](/assets/img/linux/file/raid/raid1.png){: width="972" height="589"}
          (사진 출처 : https://medium.com/@PITSGlobalDataRecoveryServices/raid-1-explained-the-power-of-duplicate-data-53e9dbeb92b1)

  - RAID 0+1
    - RAID 0과 RAID 1을 결합하는 방식
    - 최소 4개 이상의 디스크에서 먼저 2개씩 RAID 0 (스트라이핑)으로 묶고 이것을 다시 RAID 1(미러링)으로 결합하는 방식.

    ![Desktop View](/assets/img/linux/file/raid/raid10.png){: width="972" height="589"}
    (사진 출처 : https://medium.com/@PITSGlobalDataRecoveryServices/raid-10-explained-d7ef684c4035)

  - RAID 2
    - 오류 정정을 위해 해밍 코드(Hamming Code)를 사용하는 방식으로 비트 단위에 해밍 코드를 적용
    - 최근 디스크 드라이브에는 기본적으로 오류 검출 가능이 있으므로 거의 사용 안함
    - * 해밍 코드(Hamming Code) : 데이터의 오류를 검출하고 수정하는 오류 수정 코드

  - RAID 3/4
    - 하나의 디스크를 패리티(Parity) 정보를 위해 사용하고, 나머지 디스크에 데이터를 균등하게 분산 저장하는 방식
    - 읽기 성능은 RAID 0과 비슷하나, 쓰기는 패리티 처리로 인해 일부 성능이 저하됨
    - 하나의 디스크에 오류가 발생하면 패리티 디스크를 통해 복구할 수 있음
    - RAID 4는 RAID 3과 같으나, 블록 단위로 분산 저장하는 차이가 있으며, 모든 블록이 각 디스크에 균등하게 저장되진 않음
    - 병목 현상(Bottle Neck)이 발생하면 성능 저하가 발생할 수 있음
    - * 패리티(Parity) : 정보의 전달 과정에서 오류가 생겼는지를 검사하기 위해 추가되는 비트
    - * 병목 현상(Bottle Neck) : 시스템의 성능이나 용량이 하나의 구성요소로 인해 제한을 받는 현상을 말함

  - RAID 5
    - 3개 이상의 디스크를 사용하여 하나의 디스크처럼 사용하고, 각각의 디스크에 패리티 정보를 가지고 있는 방식
    - 하나의 디스크에 오류가 발생해도 다른 두 개의 디스크를 통해 복구할 수 있음
    - 패리티 디스크를 별도로 사용하지 않으므로 병목 현상이 발생하지 않음

    ![Desktop View](/assets/img/linux/file/raid/raid5.png){: width="972" height="589"}
    (사진 출처 : https://recoverit.wondershare.com/windows-tips/what-is-raid-5.html)

  - RAID 6
    - 하나의 패리티를 두 개의 디스크에 분산 저장하는 방식
    - 패리티를 이중으로 저장하기 때문에 두 개의 디스크에 오류가 발생해도 복구할 수 있음
    - 쓰기 속도는 패리티를 10번 쓰기 때문에 느려질 수 있지만, 안정성은 높아짐

    ![Desktop View](/assets/img/linux/file/raid/raid6.png){: width="972" height="589"}
    (사진 출처 : https://phoenixnap.com/kb/raid-levels-and-types)


