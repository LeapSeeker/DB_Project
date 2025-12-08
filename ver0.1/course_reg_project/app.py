# app.py
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import db

app = Flask(__name__)
app.secret_key = "super-secret-key"  # 아무 문자열이나, 세션용

# 루트 → 로그인으로 리다이렉트
@app.route("/")
def index():
    return redirect(url_for("login"))

# 로그인 화면
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    login_id = request.form.get("login_id")
    password = request.form.get("password")
    user = db.get_user(login_id, password)

    if not user:
        return render_template("login.html", 
                               error="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    session["user_id"] = user["user_id"]
    session["login_id"] = user["login_id"]
    session["role"] = user["role"]
    session["student_id"] = user.get("student_id")
    session["prof_id"] = user.get("prof_id")
    session["staff_id"] = user.get("staff_id")

    if user["role"] == "student":
        return redirect(url_for("student_dashboard"))
    elif user["role"] == "professor":
        return redirect(url_for("prof_dashboard"))
    else:
        return redirect(url_for("staff_dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# 학생 대시보드
@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") != "student":
        return render_template("error.html", message="학생 계정만 접근할 수 있습니다.")

    student_id = session.get("student_id")
    student = db.get_student(student_id)

    # 신청한 교과목 목록 (요일/교시/강의실/교수 포함)
    regs = db.get_student_registrations(student_id)
    reg_count = len(regs)

    # 시간표 교시 범위 
    max_period = 12

    return render_template(
        "student/dashboard.html",
        student=student,
        reg_count=reg_count,
        regs=regs,
        max_period=max_period,
    )

# 교수 대시보드
@app.route("/professor/dashboard")
def prof_dashboard():
    if session.get("role") != "professor":
        return render_template("error.html", message="교수 계정만 접근할 수 있습니다.")

    prof_id = session.get("prof_id")
    professor = db.get_professor(prof_id)   # 새로 추가하는 부분

    return render_template(
        "professor/dashboard.html",
        professor=professor
    )

# 교직원 대시보드
@app.route("/staff/dashboard")
def staff_dashboard():
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")
    return render_template("staff/dashboard.html")

# 교과목 + 강의 추가 (교직원 전용)
@app.route("/staff/course/new", methods=["GET", "POST"])
def staff_course_new():
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    professors = db.get_professors()
    rooms = db.get_rooms()
    message = None
    error = None

    if request.method == "POST":
        form = request.form
        data = {
            "course_id": form.get("course_id"),
            "course_name": form.get("course_name"),
            "credit": form.get("credit"),
            "min_grade": form.get("min_grade"),
            "lecture_id": form.get("lecture_id"),
            "prof_id": form.get("prof_id"),
            "room_id": form.get("room_id"),
            "day_of_week": form.get("day_of_week"),
            "start_period": form.get("start_period"),
            "end_period": form.get("end_period"),
            "program_type": form.get("program_type"),
        }

        required = ["course_id", "course_name", "credit",
                    "lecture_id", "prof_id", "room_id",
                    "day_of_week", "start_period", "end_period", "program_type"]
        if any(not data[k] for k in required):
            error = "필수 항목을 모두 입력해 주세요."
        else:
            try:
                db.insert_course_and_lecture(data, session.get("staff_id"))
                message = "교과목과 강의가 성공적으로 추가되었습니다."
            except Exception as e:
                print(e)
                error = "DB 처리 중 오류가 발생했습니다."

    return render_template(
        "staff/course_new.html",
        professors=professors,
        rooms=rooms,
        message=message,
        error=error,
    )

@app.route("/staff/course/<lecture_id>")
def staff_course_detail(lecture_id):
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    lecture = db.get_lecture_detail_with_room_and_prof(lecture_id)
    students = db.get_registration_students_by_lecture(lecture_id)

    return render_template(
        "course_detail.html",
        lecture=lecture,
        students=students,
    )

@app.route("/staff/courses")
def staff_courses():
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    courses = db.get_staff_courses()
    return render_template("staff/course_list.html", courses=courses)


@app.route("/staff/course/<lecture_id>/edit", methods=["GET", "POST"])
def staff_course_edit(lecture_id):
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    professors = db.get_professors()
    rooms = db.get_rooms()
    error = None
    message = None

    if request.method == "POST":
        form = request.form
        data = {
            "course_id": form.get("course_id"),
            "course_name": form.get("course_name"),
            "credit": form.get("credit"),
            "min_grade": form.get("min_grade"),
            "lecture_id": lecture_id,
            "prof_id": form.get("prof_id"),
            "room_id": form.get("room_id"),
            "day_of_week": form.get("day_of_week"),
            "start_period": form.get("start_period"),
            "end_period": form.get("end_period"),
            "program_type": form.get("program_type"),
        }

        try:
            db.update_course_and_lecture(data)
            message = "수정이 완료되었습니다."
        except Exception as e:
            print(e)
            error = "DB 처리 중 오류가 발생했습니다."

        # 다시 상세를 읽어와서 새 값으로 렌더링
        detail = db.get_course_and_lecture(lecture_id)
        return render_template(
            "staff/course_edit.html",
            detail=detail,
            professors=professors,
            rooms=rooms,
            error=error,
            message=message,
        )

    # GET: 수정 폼 처음 열기
    detail = db.get_course_and_lecture(lecture_id)
    if not detail:
        return render_template("error.html", message="해당 강의를 찾을 수 없습니다.")

    return render_template(
        "staff/course_edit.html",
        detail=detail,
        professors=professors,
        rooms=rooms,
        error=error,
        message=message,
    )

@app.route("/staff/course/<lecture_id>/delete", methods=["POST"])
def staff_course_delete(lecture_id):
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    try:
        db.delete_course_and_lecture(lecture_id)
    except Exception as e:
        print(e)
        return render_template("error.html", message="삭제 중 오류가 발생했습니다.")

    return redirect(url_for("staff_courses"))


@app.route("/api/course/<course_id>")
def api_course(course_id):
    """course_id로 과목 정보 조회해서 JSON으로 반환"""
    row = db.get_course_by_id(course_id)
    if row:
        return jsonify({
            "exists": True,
            "course_id": row["course_id"],
            "course_name": row["course_name"],
            "credit": row["credit"],
            "min_grade": row["min_grade"],
        })
    else:
        return jsonify({"exists": False})

@app.route("/staff/courses/by-prof")
def staff_courses_by_prof():
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    professors = db.get_professors()
    selected_prof_id = request.args.get("prof_id")
    lectures = []

    if selected_prof_id:
        lectures = db.get_courses_by_prof(selected_prof_id)

    return render_template(
        "staff/courses_by_prof.html",
        professors=professors,
        selected_prof_id=selected_prof_id,
        lectures=lectures,
    )

@app.route("/staff/courses/by-student")
def staff_courses_by_student():
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    students = db.get_students()
    selected_student_id = request.args.get("student_id")
    lectures = []

    if selected_student_id:
        lectures = db.get_courses_by_student(selected_student_id)

    return render_template(
        "staff/courses_by_student.html",
        students=students,
        selected_student_id=selected_student_id,
        lectures=lectures,
    )

@app.route("/staff/rooms")
def staff_rooms():
    if session.get("role") != "staff":
        return render_template("error.html", message="교직원 계정만 접근할 수 있습니다.")

    rooms = db.get_rooms()
    selected_room_id = request.args.get("room_id")
    lectures = []

    if selected_room_id:
        lectures = db.get_lectures_by_room(selected_room_id)

    return render_template(
        "staff/rooms.html",
        rooms=rooms,
        selected_room_id=selected_room_id,
        lectures=lectures,
    )

@app.route("/professor/lectures")
def prof_lectures():
    if session.get("role") != "professor":
        return render_template("error.html", message="교수 계정만 접근할 수 있습니다.")

    prof_id = session.get("prof_id")
    prof = db.get_professor(prof_id)
    lectures = db.get_prof_lectures(prof_id)

    # 요약 정보 계산
    lecture_count  = len(lectures)
    room_set       = { (l["building"], l["room_id"]) for l in lectures }
    building_set   = { l["building"] for l in lectures }
    room_count     = len(room_set)
    building_count = len(building_set)

    summary = {
        "lecture_count": lecture_count,
        "room_count": room_count,
        "building_count": building_count,
    }

    return render_template(
        "professor/lectures.html",
        prof=prof,
        lectures=lectures,
        summary=summary,
    )

@app.route("/professor/lecture/<lecture_id>/students")
def prof_lecture_students(lecture_id):
    if session.get("role") != "professor":
        return render_template("error.html", message="교수 계정만 접근할 수 있습니다.")

    # (선택) 내 강의가 아니면 막기
    prof_id = session.get("prof_id")
    lecture = db.get_lecture_info(lecture_id)
    if not lecture:
        return render_template("error.html", message="해당 강의를 찾을 수 없습니다.")
    if lecture["prof_id"] != prof_id:
        return render_template("error.html", message="본인이 담당하지 않는 강의입니다.")

    students = db.get_lecture_students(lecture_id)

    return render_template(
        "professor/lecture_students.html",
        lecture=lecture,
        students=students,
    )

@app.route("/professor/lectures/by-place")
def prof_lectures_by_place():
    if session.get("role") != "professor":
        return render_template("error.html", message="교수 계정만 접근할 수 있습니다.")

    prof_id = session.get("prof_id")
    prof = db.get_professor(prof_id)

    buildings = db.get_buildings_for_prof(prof_id)
    rooms     = db.get_rooms_for_prof(prof_id)

    selected_building = request.args.get("building")
    selected_room_id  = request.args.get("room_id")

    lectures = []
    if selected_room_id:
        lectures = db.get_prof_lectures_by_room(prof_id, selected_room_id)
    elif selected_building:
        lectures = db.get_prof_lectures_by_building(prof_id, selected_building)

    return render_template(
        "professor/lectures_by_place.html",
        prof=prof,
        buildings=buildings,
        rooms=rooms,
        selected_building=selected_building,
        selected_room_id=selected_room_id,
        lectures=lectures,
    )

@app.route("/student/registrations")
def student_registrations():
    if session.get("role") != "student":
        return render_template("error.html", message="학생 계정만 접근할 수 있습니다.")

    student_id = session.get("student_id")
    student = db.get_student(student_id)
    regs = db.get_student_registrations(student_id)

    return render_template(
        "student/registrations.html",
        student=student,
        regs=regs
    )

@app.route("/student/registration/delete", methods=["POST"])
def student_registration_delete():
    if session.get("role") != "student":
        return render_template("error.html", message="학생 계정만 접근할 수 있습니다.")

    student_id = session.get("student_id")
    lecture_id = request.form.get("lecture_id")

    db.delete_registration(student_id, lecture_id)
    return redirect(url_for("student_registrations"))

@app.route("/student/change/<lecture_id>", methods=["GET", "POST"])
def student_change_registration(lecture_id):
    # 1) 권한 체크
    if session.get("role") != "student":
        return render_template("error.html", message="학생 계정만 접근할 수 있습니다.")

    student_id = session.get("student_id")

    # 2) 현재 신청한 분반 정보 조회
    current = db.get_lecture_by_id(lecture_id)
    if not current:
        return render_template("error.html", message="해당 강의를 찾을 수 없습니다.")

    # (선택) 정말 이 학생이 이 분반을 신청했는지 확인
    if not db.is_registered(student_id, lecture_id):
        return render_template("error.html", message="해당 분반을 신청한 학생만 정정할 수 있습니다.")

    # 3) 같은 과목(course_id)의 다른 분반 목록 조회
    all_sections = db.get_lectures_by_course(current["course_id"])
    alternatives = [lec for lec in all_sections if lec["lecture_id"] != lecture_id]

    if request.method == "GET":
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error=None,
            message=None,
        )
    
    new_lecture_id = request.form.get("new_lecture_id")

    if not new_lecture_id:
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="변경할 분반을 선택해 주세요.",
            message=None,
        )

    if new_lecture_id == lecture_id:
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="현재 신청된 분반과 동일한 분반으로는 정정할 수 없습니다.",
            message=None,
        )

    # 새 분반 정보 확인
    new_lecture = db.get_lecture_by_id(new_lecture_id)
    if not new_lecture:
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="선택한 분반 정보를 찾을 수 없습니다.",
            message=None,
        )

    # 같은 과목인지 검증 (course_id 동일해야 정정 가능)
    if new_lecture["course_id"] != current["course_id"]:
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="같은 과목의 다른 분반으로만 정정할 수 있습니다.",
            message=None,
        )

    # 1) 시간표 충돌 검사 (기존 함수 그대로 사용)
    if db.has_time_conflict(student_id, new_lecture_id):
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="선택한 분반은 기존 시간표와 시간이 겹쳐 수강이 불가능합니다.",
            message=None,
        )

    # 2) 정원 초과 검사
    if db.is_lecture_full(new_lecture_id):
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="선택한 분반은 정원이 마감되어 정정할 수 없습니다.",
            message=None,
        )

    # 3) 조건 통과 → 실제 정정 수행 (트랜잭션 함수)
    ok = db.update_registration_change(student_id, lecture_id, new_lecture_id)
    if not ok:
        return render_template(
            "student/change.html",
            current=current,
            alternatives=alternatives,
            error="정정 처리 중 오류가 발생했습니다. 다시 시도해 주세요.",
            message=None,
        )

    # 성공 → 신청 교과목 목록으로 이동
    return redirect(url_for("student_registrations"))

@app.route("/student/timetable")
def student_timetable():
    if session.get("role") != "student":
        return render_template("error.html", message="학생 계정만 접근할 수 있습니다.")

    student_id = session.get("student_id")
    student = db.get_student(student_id)
    regs = db.get_student_registrations(student_id)


    max_period = 12

    return render_template(
        "student/timetable.html",
        student=student,
        regs=regs,
        max_period=max_period,
    )

@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if session.get("role") != "student":
        return render_template("error.html", message="학생 계정만 접근할 수 있습니다.")

    student_id = session.get("student_id")
    student = db.get_student(student_id)
    grade = student.get("grade")

    # 학번에서 반 추출 → 7번째 글자(인덱스 6)를 반으로 사용
    class_no = None
    if student_id and len(student_id) >= 7 and student_id[6].isdigit():
        try:
            class_no = int(student_id[6])
        except ValueError:
            class_no = None

    lectures = db.get_lectures_for_registration(student_id)

    # 이미 신청한 강의 목록 → 중복 신청/버튼 상태 표시용
    regs = db.get_student_registrations(student_id)
    registered_ids = {r["lecture_id"] for r in regs}

    # 강의 정렬 우선순위 함수
    def calc_priority(lec: dict):
        tgt_grade = lec.get("target_grade", grade)
        lec_class = lec.get("class_no", 0)

        if tgt_grade == grade and class_no is not None and lec_class == class_no:
            return (0, tgt_grade, lec_class, lec["lecture_id"])
        elif tgt_grade == grade:
            return (1, tgt_grade, lec_class, lec["lecture_id"])
        else:
            return (2, tgt_grade, lec_class, lec["lecture_id"])

    lectures = sorted(lectures, key=calc_priority)

    year = 2025
    term = "2학기"

    #  GET → 화면 보여주기
    if request.method == "GET":
        return render_template(
            "student/register.html",
            student=student,
            grade=grade,
            class_no=class_no,
            year=year,
            term=term,
            lectures=lectures,
            registered_ids=registered_ids,
            error=None,
        )   
    
    # POST → 수강 신청 처리
    lecture_id = request.form.get("lecture_id")

    # 이미 신청한 강의인지 중복 체크
    if lecture_id in registered_ids:
        return render_template(
            "student/register.html",
            student=student,
            grade=grade,
            class_no=class_no,
            year=year,
            term=term,
            lectures=lectures,
            registered_ids=registered_ids,
            error="이미 신청한 강의입니다.",
        )

    # 시간표 충돌 검사
    if db.has_time_conflict(student_id, lecture_id):
        return render_template(
            "student/register.html",
            student=student,
            grade=grade,
            class_no=class_no,
            year=year,
            term=term,
            lectures=lectures,
            registered_ids=registered_ids,
            error="선택한 강의와 같은 시간대에 이미 신청한 강의가 있어 수강이 불가능합니다.",
        )

    db.insert_registration(student_id, lecture_id)
    return redirect(url_for("student_register"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)