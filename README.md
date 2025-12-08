# DB_Project
[목차]
1. 프로젝트 개요
2. 주요 기능
3. 기술 스택
4. 시스템 구조
5. DB 스키마 요약
6. 화면 구성
7. 폴더 구조
8. 실행 방법
9. 개선 예정 항목

[프로젝트 개요]
본 프로젝트는 Flask 기반 웹 서버와 MySQL 데이터베이스를 활용해 
학생-교수-교직원의 3권한을 지원하는 수강신청 플랫폼이다.

구현된 기능
- 학생의 수강신청 / 취소 / 분반 정정
- 시간표 자동 생성
- 교수의 담당 강의 조회 및 수강 학생 목록 확인
- 교직원의 교과목 CRUD 및 다양한 조건 기반 조회
- 사용자 로그인 및 역할 기반 인증

[주요 기능]
학생
- 로그인
- 수강신청 가능한 강의 목록 조회
- 수강신청 / 취소
- 분반 정정(같은 과목 내 다른 분반으로 변경)
- 신청한 강의를 기반으로 자동 시간표 생성
- 개인 수강내역 조회

교수
- 담당 강의 목록 조회
- 강의별 수강 학생 목록 조회
- 건물/강의실 기준 내 강의 조회

교직원
- 교과목 + 강의 등록(신규 추가)
- 강의 정보 수정 / 삭제
- 교수별 강의 조회
- 학생별 수강내역 조회
- 강의실별 사용 시간표 확인

[기술 스택]
Backend
- Python 3.13.1
- Flask
- Jinja2 Template Engine
- PyMySQL

Database
- MySQL 8.0
- InnoDB Storage Engine

Frontend
- HTML5 / CSS3 (Custom UI)
- Jinja Template

[시스템 구조]
구조 개요
Flask Web Server
 ├── app.py        # 라우팅 및 주요 기능 처리
 ├── db.py         # DB 연결 및 SQL 처리 함수
 ├── templates/    # HTML 화면
 └── static/       # 필요 시 정적 파일

역할별 접근 플로우
- user.login -> role에 따라 dashboard 분기
  - 학생 -> /student/*
  - 교수 -> /professor/*
  - 교직원 -> /staff/*

 [DB 스키마 요약]
 주요 테이블
| 테이블           | 설명                                    
| ---------------- | ------------------------------------------ 
| user             | 로그인 정보 (role: student/professor/staff) 
| student          | 학생 정보 및 학년/과정                      
| professor        | 교수 정보                                  
| staff            | 교직원 정보                                
| course           | 과목 정보 (학점, 명칭 등)                  
| lecture          | 실제 개설된 강의(분반 정보 포함)           
| registration     | 학생의 수강신청 결과     

간단 ERD (요약형)
user ─── 1:1 ── student
user ─── 1:1 ── professor
user ─── 1:1 ── staff

course ─── 1:N ─── lecture ─── N:N(through registration) ─── student
room ─── 1:N ─── lecture
professor ─── 1:N ─── lecture

[화면 구성]
학생 화면
- Dashboard
- 수강신청 페이지
- 신청 내역 / 취소 / 정정
- 시간표

교수 화면
- 담당 강의 목록
- 강의별 수강 학생 조회
- 강의실 / 건물 기준 조회

교직원 화면
- 교과목 등록 / 수정 / 삭제
- 교수별 강의 조회
- 학생별 수강내역 조회
- 강의실 시간표 조회

[폴더 구조]
project/
├── app.py
├── db.py
├── DB.sql
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── error.html
│   ├── course_detail.html
│   ├── student/
│   │   ├── dashboard.html
│   │   ├── register.html
│   │   ├── registrations.html
│   │   ├── change.html
│   │   └── timetable.html
│   ├── professor/
│   │   ├── dashboard.html
│   │   ├── lectures.html
│   │   ├── lecture_students.html
│   │   └── lectures_by_place.html
│   └── staff/
│       ├── dashboard.html
│       ├── course_new.html
│       ├── course_list.html
│       ├── course_edit.html
│       ├── courses_by_prof.html
│       ├── courses_by_student.html
│       └── rooms.html
└── __pycache__/  (자동 생성, 버전 관리 X)

[실행 방법]
1) 패키지 설치
- pip install flask pymysql

2) MySQL에 데이터베이스 생성
- source DB.sql
또는 Workbench에서 직접 실행

3) Flask 서버 실행
- python app.py

4) 브라우저 접속
- http://localhost:5000
- CTRL+클릭으로 이동

[개선 예정 항목]
- 미정
