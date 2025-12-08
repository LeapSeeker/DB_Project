# db.py
import pymysql

def get_connection():
    conn = pymysql.connect(
        host="127.0.0.1",  # MySQL 서버 호스트이름
        user="root",        # MySQL 사용자
        password="20240B208",    # MySQL 비밀번호(본인 설정값)
        db="수강",        # DB 이름
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return conn

def get_user(login_id, password):
    """로그인 아이디/비밀번호로 user 테이블에서 한 명 조회"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT user_id, login_id, role,
                   student_id, prof_id, staff_id
            FROM user
            WHERE login_id = %s AND password = %s
            """
            cur.execute(sql, (login_id, password))
            return cur.fetchone()

def get_professors():
    """교수 목록 (드롭다운용)"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT prof_id, name FROM professor ORDER BY name")
            return cur.fetchall()

def get_rooms():
    """강의실 목록 (드롭다운용)"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT room_id, room_name FROM room ORDER BY room_id")
            return cur.fetchall()

def insert_course_and_lecture(data, staff_id):
    """과목 + 강의 한 번에 추가"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # 이 course_id가 이미 있는지 확인
            cur.execute(
                "SELECT 1 FROM course WHERE course_id = %s",
                (data["course_id"],),
            )
            exists = cur.fetchone() is not None

            # 과목이 없을 때만 INSERT
            if not exists:
                sql_course = """
                    INSERT INTO course (course_id, course_name, 
                                        credit, min_grade, staff_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(
                    sql_course,
                    (
                        data["course_id"],
                        data["course_name"],
                        int(data["credit"]),
                        int(data["min_grade"]) if data["min_grade"] else None,
                        staff_id,
                    ),
                )

            # 강의는 항상 INSERT (분반 추가 가능)
            sql_lecture = """
                INSERT INTO lecture (
                    lecture_id, day_of_week, start_period, end_period,
                    prof_id, course_id, room_id, program_type
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(
                sql_lecture,
                (
                    data["lecture_id"],
                    data["day_of_week"],
                    int(data["start_period"]),
                    int(data["end_period"]),
                    data["prof_id"],
                    data["course_id"],  
                    data["room_id"],
                    data["program_type"],
                ),
            )
        conn.commit()

def get_staff_courses():
    """교직원이 보는 교과목+강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                c.course_id, c.course_name,
                c.credit, c.min_grade,
                l.lecture_id, l.day_of_week,
                l.start_period, l.end_period, l.program_type,
                p.name AS prof_name,
                r.room_id, r.room_name
            FROM course c
            JOIN lecture l ON c.course_id = l.course_id
            JOIN professor p ON l.prof_id = p.prof_id
            JOIN room r ON l.room_id = r.room_id
            ORDER BY c.course_id
            """
            cur.execute(sql)
            return cur.fetchall()


def get_course_and_lecture(lecture_id):
    """특정 강의(lecture_id)의 과목+강의 상세 정보"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                c.course_id, c.course_name,
                c.credit, c.min_grade,
                l.lecture_id, l.day_of_week,
                l.start_period, l.end_period,
                l.program_type, l.prof_id, l.room_id
            FROM course c
            JOIN lecture l ON c.course_id = l.course_id
            WHERE l.lecture_id = %s
            """
            cur.execute(sql, (lecture_id,))
            return cur.fetchone()


def update_course_and_lecture(data):
    """과목 + 강의 정보 수정"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # 과목 수정
            sql_course = """
                UPDATE course
                SET course_name = %s,
                    credit = %s,
                    min_grade = %s
                WHERE course_id = %s
            """
            cur.execute(
                sql_course,
                (
                    data["course_name"],
                    int(data["credit"]),
                    int(data["min_grade"]) if data["min_grade"] else None,
                    data["course_id"],
                ),
            )

            # 강의 수정
            sql_lecture = """
                UPDATE lecture
                SET day_of_week = %s,
                    start_period = %s,
                    end_period = %s,
                    prof_id = %s,
                    room_id = %s,
                    program_type = %s
                WHERE lecture_id = %s
            """
            cur.execute(
                sql_lecture,
                (
                    data["day_of_week"],
                    int(data["start_period"]),
                    int(data["end_period"]),
                    data["prof_id"],
                    data["room_id"],
                    data["program_type"],
                    data["lecture_id"],
                ),
            )
        conn.commit()

def delete_course_and_lecture(lecture_id):
    """수강신청 → 강의 → 과목 순서로 삭제 (단일 강의/과목 구조 가정)"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # 먼저 강의 정보에서 course_id 가져오기
            cur.execute(
                "SELECT course_id FROM lecture WHERE lecture_id = %s",
                (lecture_id,),
            )
            row = cur.fetchone()
            if not row:
                return
            course_id = row["course_id"]

            # 수강신청 삭제
            cur.execute(
                "DELETE FROM registration WHERE lecture_id = %s",
                (lecture_id,),
            )

            # 강의 삭제
            cur.execute(
                "DELETE FROM lecture WHERE lecture_id = %s",
                (lecture_id,),
            )

            # 과목 삭제 (이 과목을 쓰는 다른 강의가 없을 때만)
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM lecture WHERE course_id = %s",
                (course_id,),
            )
            cnt = cur.fetchone()["cnt"]
            if cnt == 0:
                cur.execute(
                    "DELETE FROM course WHERE course_id = %s",
                    (course_id,),
                )
        conn.commit()

def get_course_by_id(course_id):
    """course_id로 과목 1개 조회"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT course_id, course_name, credit, min_grade
            FROM course
            WHERE course_id = %s
            """
            cur.execute(sql, (course_id,))
            return cur.fetchone()
        
def get_students():
    """학생 선택용 간단 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT student_id, name
            FROM student
            ORDER BY name
            """
            cur.execute(sql)
            return cur.fetchall()

def get_courses_by_prof(prof_id):
    """특정 교수의 담당 강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                c.course_id, c.course_name,
                l.day_of_week, l.start_period, l.end_period,
                r.room_id, r.room_name,
                l.program_type
            FROM lecture l
            JOIN course c ON l.course_id = c.course_id
            JOIN room r ON l.room_id = r.room_id
            WHERE l.prof_id = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (prof_id,))
            return cur.fetchall()

def get_courses_by_student(student_id):
    """특정 학생의 수강신청 강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                s.student_id, s.name AS student_name,
                c.course_id, c.course_name,
                l.lecture_id, l.day_of_week,
                l.start_period, l.end_period,
                p.name AS prof_name,
                r.room_id, r.room_name,
                l.program_type
            FROM registration reg
            JOIN student s ON reg.student_id = s.student_id
            JOIN lecture l ON reg.lecture_id = l.lecture_id
            JOIN course c ON l.course_id = c.course_id
            JOIN professor p ON l.prof_id = p.prof_id
            JOIN room r ON l.room_id = r.room_id
            WHERE reg.student_id = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (student_id,))
            return cur.fetchall()


def get_lectures_by_room(room_id):
    """특정 강의실에서 열리는 강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                c.course_id, c.course_name,
                p.name AS prof_name,
                l.day_of_week, l.start_period,
                l.end_period, l.program_type
            FROM lecture l
            JOIN course c ON l.course_id = c.course_id
            JOIN professor p ON l.prof_id = p.prof_id
            WHERE l.room_id = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (room_id,))
            return cur.fetchall()

def get_prof_lectures(prof_id):
    """교수 한 명의 담당 강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                c.course_id, c.course_name,
                l.day_of_week, l.start_period,
                l.end_period, l.program_type,
                r.room_id, r.room_name, r.building
            FROM lecture l
            JOIN course c ON l.course_id = c.course_id
            JOIN room   r ON l.room_id = r.room_id
            WHERE l.prof_id = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (prof_id,))
            return cur.fetchall()
        
def get_professor(prof_id):
    """교수 한 명 정보"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = "SELECT prof_id, name, dept_id FROM professor WHERE prof_id = %s"
            cur.execute(sql, (prof_id,))
            return cur.fetchone()

def get_lecture_info(lecture_id):
    """강의 한 개의 상세정보 (과목/교수/강의실/건물 등)"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                l.day_of_week,
                l.start_period,
                l.end_period,
                l.program_type,
                c.course_id,
                c.course_name,
                r.room_id,
                r.room_name,
                r.building,
                p.prof_id,
                p.name AS prof_name
            FROM lecture l
            JOIN course    c ON l.course_id = c.course_id
            JOIN room      r ON l.room_id = r.room_id
            JOIN professor p ON l.prof_id = p.prof_id
            WHERE l.lecture_id = %s
            """
            cur.execute(sql, (lecture_id,))
            return cur.fetchone()

def get_lecture_students(lecture_id):
    """특정 강의에 수강신청한 학생 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                s.student_id,
                s.name AS student_name,
                s.grade,
                s.program_type,
                d.dept_name
            FROM registration reg
            JOIN student    s ON reg.student_id = s.student_id
            JOIN department d ON s.dept_id = d.dept_id
            WHERE reg.lecture_id = %s
            ORDER BY s.name
            """
            cur.execute(sql, (lecture_id,))
            return cur.fetchall()


def get_buildings_for_prof(prof_id):
    """해당 교수가 수업하는 건물 목록 (중복 제거)"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT DISTINCT r.building
            FROM lecture l
            JOIN room r ON l.room_id = r.room_id
            WHERE l.prof_id = %s
            ORDER BY r.building
            """
            cur.execute(sql, (prof_id,))
            return cur.fetchall()


def get_rooms_for_prof(prof_id):
    """해당 교수가 사용하는 강의실 목록 (중복 제거)"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT DISTINCT r.room_id, r.room_name, r.building
            FROM lecture l
            JOIN room r ON l.room_id = r.room_id
            WHERE l.prof_id = %s
            ORDER BY r.building, r.room_id
            """
            cur.execute(sql, (prof_id,))
            return cur.fetchall()


def get_prof_lectures_by_building(prof_id, building):
    """해당 교수가 특정 건물에서 담당하는 강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
                l.lecture_id,
                c.course_id, c.course_name,
                l.day_of_week, l.start_period, l.end_period, l.program_type,
                r.room_id, r.room_name, r.building
            FROM lecture l
            JOIN course c ON l.course_id = c.course_id
            JOIN room   r ON l.room_id = r.room_id
            WHERE l.prof_id = %s
              AND r.building = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (prof_id, building))
            return cur.fetchall()


def get_prof_lectures_by_room(prof_id, room_id):
    """해당 교수가 특정 강의실에서 담당하는 강의 목록"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                c.course_id, c.course_name,
                l.day_of_week, l.start_period, l.end_period, l.program_type,
                r.room_id, r.room_name, r.building
            FROM lecture l
            JOIN course c ON l.course_id = c.course_id
            JOIN room   r ON l.room_id = r.room_id
            WHERE l.prof_id = %s
              AND r.room_id = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (prof_id, room_id))
            return cur.fetchall()

def get_student(student_id):
    """학생 한 명 정보"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = "SELECT student_id, name, grade, program_type, dept_id FROM student WHERE student_id = %s"
            cur.execute(sql, (student_id,))
            return cur.fetchone()

def get_student_registrations(student_id):
    """
    학생이 신청한 교과목 목록 조회
    (과목, 강의, 교수, 건물/강의실, 시간 모두 포함)
    """
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                reg.lecture_id,
                c.course_id, c.course_name,
                l.day_of_week, l.start_period, l.end_period, l.program_type,
                p.prof_id, p.name AS prof_name,
                r.room_id, r.room_name, r.building
            FROM registration reg
            JOIN lecture   l ON reg.lecture_id = l.lecture_id
            JOIN course    c ON l.course_id   = c.course_id
            JOIN professor p ON l.prof_id     = p.prof_id
            JOIN room      r ON l.room_id     = r.room_id
            WHERE reg.student_id = %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (student_id,))
            return cur.fetchall()

def get_lectures_for_registration(student_id):
    """
    수강신청 화면용.
    - 학생의 program_type(전문학사/전공심화/P-TECH)에 맞는 강의만
    - 학생 학년(s.grade)과 과목 최소학년(c.min_grade)을 비교해서
      '내 학년 과목'이 위쪽에 나오도록 정렬
    """
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                c.course_id,
                c.course_name,
                c.min_grade,             -- 최소 학년
                l.day_of_week,
                l.start_period,
                l.end_period,
                l.program_type,
                p.name AS prof_name,
                r.room_id,
                r.room_name,
                r.building,
                CASE
                    WHEN reg.student_id IS NULL THEN 0
                    ELSE 1
                END AS is_registered
            FROM student s
            JOIN lecture   l ON l.program_type = s.program_type
            JOIN course    c ON l.course_id   = c.course_id
            JOIN professor p ON l.prof_id     = p.prof_id
            JOIN room      r ON l.room_id     = r.room_id
            LEFT JOIN registration reg
              ON reg.student_id = s.student_id
             AND reg.lecture_id = l.lecture_id
            WHERE s.student_id = %s
            ORDER BY
              CASE
                WHEN c.min_grade = s.grade THEN 0   -- 내 학년 과목 (예: 2학년에게 2학년 과목)
                WHEN c.min_grade IS NULL THEN 2     -- 학년 제한 없는 과목
                ELSE 1                              -- 다른 학년 과목
              END,
              c.course_id,
              l.day_of_week,
              l.start_period
            """
            cur.execute(sql, (student_id,))
            return cur.fetchall()

def delete_registration(student_id, lecture_id):
    """수강 취소"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            DELETE FROM registration
            WHERE student_id = %s AND lecture_id = %s
            """
            cur.execute(sql, (student_id, lecture_id))
            conn.commit()


def get_lectures_same_course(lecture_id):
    """
    정정용: 현재 lecture와 같은 과목(course_id)의 다른 분반 리스트
    (본인 분반 제외)
    """
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # 현재 강의의 과목ID 먼저 구하기
            sql_course = """
            SELECT course_id
            FROM lecture
            WHERE lecture_id = %s
            """
            cur.execute(sql_course, (lecture_id,))
            row = cur.fetchone()
            if not row:
                return []

            course_id = row["course_id"]

            sql = """
            SELECT
                l.lecture_id,
                c.course_id,
                c.course_name,
                l.day_of_week,
                l.start_period,
                l.end_period,
                l.program_type,
                p.name AS prof_name,
                r.room_id,
                r.room_name,
                r.building
            FROM lecture l
            JOIN course    c ON l.course_id = c.course_id
            JOIN professor p ON l.prof_id   = p.prof_id
            JOIN room      r ON l.room_id   = r.room_id
            WHERE l.course_id = %s
              AND l.lecture_id <> %s
            ORDER BY l.day_of_week, l.start_period
            """
            cur.execute(sql, (course_id, lecture_id))
            return cur.fetchall()

def has_time_conflict(student_id, lecture_id):
    """
    해당 학생이 이미 신청한 강의들 중에서
    새로 신청하려는 lecture_id와 시간(요일/교시)이 겹치는 게 있는지 검사
    겹치면 True, 아니면 False 반환
    """
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT 1
            FROM registration r
            JOIN lecture l1 ON l1.lecture_id = r.lecture_id  
            JOIN lecture l2 ON l2.lecture_id = %s            
            WHERE r.student_id = %s
              AND l1.day_of_week = l2.day_of_week            
              AND NOT (
                    l1.end_period   < l2.start_period        
                OR  l2.end_period   < l1.start_period       
              )
            LIMIT 1
            """
            cur.execute(sql, (lecture_id, student_id))
            row = cur.fetchone()
            return row is not None
        
def insert_registration(student_id, lecture_id):
    """수강신청 한 건 추가"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO registration (student_id, lecture_id)
            VALUES (%s, %s)
            """
            cur.execute(sql, (student_id, lecture_id))
        conn.commit()  
    finally:
        conn.close()

def get_lecture_detail_with_room_and_prof(lecture_id):
    """강의 상세정보 (과목/교수/강의실/건물 등)"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                c.course_id,
                c.course_name,
                c.credit,
                l.day_of_week,
                l.start_period,
                l.end_period,
                l.program_type,
                p.prof_id,
                p.name       AS prof_name,
                r.room_id,
                r.room_name,
                r.building
            FROM lecture l
            JOIN course c   ON c.course_id = l.course_id
            JOIN professor p ON p.prof_id = l.prof_id
            JOIN room r     ON r.room_id = l.room_id
            WHERE l.lecture_id = %s
            """
            cur.execute(sql, (lecture_id,))
            return cur.fetchone()
    finally:
        conn.close()

def get_registration_students_by_lecture(lecture_id):
    """해당 강의 신청 학생 목록 조회"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            sql = """
            SELECT
                s.student_id,
                s.name,
                s.grade,
                s.program_type,
                d.dept_name
            FROM registration r
            JOIN student s ON s.student_id = r.student_id
            LEFT JOIN department d ON d.dept_id = s.dept_id
            WHERE r.lecture_id = %s
            ORDER BY s.student_id
            """
            cur.execute(sql, (lecture_id,))
            return cur.fetchall()
    finally:
        conn.close()

def get_lecture_by_id(lecture_id):
    """lecture_id 로 강의 + 과목 + 강의실 + 교수 정보 1건 조회"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                l.course_id,
                c.course_name,
                l.day_of_week,
                l.start_period,
                l.end_period,
                l.room_id,
                r.room_name,
                r.building,
                l.prof_id,
                p.name AS prof_name,
                l.program_type
            FROM lecture l
            JOIN course c      ON l.course_id = c.course_id
            LEFT JOIN room r   ON l.room_id   = r.room_id
            LEFT JOIN professor p ON l.prof_id = p.prof_id
            WHERE l.lecture_id = %s
            """
            cur.execute(sql, (lecture_id,))
            return cur.fetchone()


def get_lectures_by_course(course_id):
    """같은 과목(course_id)의 모든 분반 목록 조회"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT
                l.lecture_id,
                l.course_id,
                c.course_name,
                l.day_of_week,
                l.start_period,
                l.end_period,
                l.room_id,
                r.room_name,
                r.building,
                l.prof_id,
                p.name AS prof_name,
                l.program_type
            FROM lecture l
            JOIN course c      ON l.course_id = c.course_id
            LEFT JOIN room r   ON l.room_id   = r.room_id
            LEFT JOIN professor p ON l.prof_id = p.prof_id
            WHERE l.course_id = %s
            ORDER BY l.lecture_id
            """
            cur.execute(sql, (course_id,))
            return cur.fetchall()


def is_registered(student_id, lecture_id):
    """해당 학생이 특정 강의를 이미 신청했는지 여부 확인"""
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT COUNT(*) AS cnt
            FROM registration
            WHERE student_id = %s AND lecture_id = %s
            """
            cur.execute(sql, (student_id, lecture_id))
            row = cur.fetchone()
            return row["cnt"] > 0


def is_lecture_full(lecture_id, limit=40):
    """
    정원 초과 여부 확인.
    현재는 registration 인원 수가 limit 이상이면 '정원 초과' 로 간주.
    (DB에 정원 컬럼이 없으므로 상수 limit 사용)
    """
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            sql = """
            SELECT COUNT(*) AS cnt
            FROM registration
            WHERE lecture_id = %s
            """
            cur.execute(sql, (lecture_id,))
            row = cur.fetchone()
            return row["cnt"] >= limit


def update_registration_change(student_id, old_lecture_id, new_lecture_id):
    """
    하나의 트랜잭션 안에서
      1) 기존 분반 삭제
      2) 새 분반 INSERT
    를 수행. 성공 시 True, 실패 시 False 반환.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # 1) 기존 신청 삭제
                sql_del = """
                DELETE FROM registration
                WHERE student_id = %s AND lecture_id = %s
                """
                cur.execute(sql_del, (student_id, old_lecture_id))

                # 2) 새 분반 신청
                sql_ins = """
                INSERT INTO registration (student_id, lecture_id)
                VALUES (%s, %s)
                """
                cur.execute(sql_ins, (student_id, new_lecture_id))
        return True

    except Exception as e:
        print("update_registration_change error:", e)
        return False