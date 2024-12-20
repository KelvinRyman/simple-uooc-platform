from flask import request, jsonify
from flask_login import LoginManager, UserMixin, login_required, current_user
import uuid
from flask_cors import CORS
from database import db, app
from model import Users, Courses, CourseEnrollments, Assignments, AssignmentSubmissions

# 配置CORS
CORS(app)


# 学生账号登录 未用過
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = Users.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({"message": "登录成功", "user_id": user.id, "role": user.role})
    return jsonify({"message": "用户名或密码错误"}), 401


# 学生账号注冊
@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "student")  # 默認是學生

    # 檢查是否存在相同的用戶名
    if Users.query.filter_by(username=username).first():
        return jsonify({"message": "用户名已存在"}), 400

    # 添加到數據庫
    new_user = Users(
        id=str(uuid.uuid4()), username=username, password=password, role=role
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "注册成功", "user_id": new_user.id})


# 建立课程
@app.route("/api/course", methods=["POST"])
def make_course():
    data = request.json
    coursetitle = data.get("title")
    teachid = data.get("teacher_id")

    # 檢查是否存在相同的ID
    # if Courses.query.filter_by(id=courseid).first():
    #     return jsonify({'message': '课程ID已存在'}), 400

    # 添加到數據庫
    new_course = Courses(title=coursetitle, teacher_id=teachid)
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "课程建立成功", "id": new_course.id})


# 课程注册
@app.route("/api/course/register", methods=["POST"])
def register_course():
    data = request.json
    course_id = data.get("course_id")
    student_id = data.get("student_id")

    if not course_id:
        return jsonify({"error": "缺少課程ID"}), 400

    # 驗證課程是否存在
    course = Courses.query.get(course_id)
    if not course:
        return jsonify({"error": "課程不存在"}), 404

    # 防止重複註冊
    existing_enrollment = CourseEnrollments.query.filter_by(
        student_id=student_id, course_id=course_id
    ).first()
    if existing_enrollment:
        return jsonify({"error": "已經註冊該課程"}), 400

    # 新增註冊記錄
    enrollment = CourseEnrollments(
        id=str(uuid.uuid4()), course_id=course_id, student_id=student_id
    )
    db.session.add(enrollment)
    db.session.commit()

    return jsonify({"message": "課程註冊成功", "id": enrollment.id}), 201


# 获取已注册课程 未用過
@app.route("/api/course/my", methods=["GET"])
def get_registered_courses():
    student_id = request.args.get("student_id")
    courses = (
        db.session.query(Courses.title, Courses.id)
        .join(CourseEnrollments, Courses.id == CourseEnrollments.course_id)
        .filter(CourseEnrollments.student_id == student_id)
        .all()
    )
    return jsonify(
        {"registered_courses": [{"id": c.id, "title": c.title} for c in courses]}
    )


# 提交作业
@app.route("/api/assignment/submit", methods=["POST"])
def submit_assignment():
    data = request.form
    assignment_id = data.get("assignment_id")
    student_id = data.get("student_id")
    content = data.get("content")
    file = request.files.get("file")

    # 保存文件 (可选)
    file_url = None
    if file:
        file_url = f"uploads/{file.filename}"
        file.save(file_url)

    submission = AssignmentSubmissions(
        id=str(uuid.uuid4()),
        assignment_id=assignment_id,
        student_id=student_id,
        content=content,
        file_url=file_url,
    )
    db.session.add(submission)
    db.session.commit()
    return jsonify({"message": "作业提交成功", "file_url": file_url})


# 获取学生待办事项 (作业列表)
@app.route("/api/assignment/pending", methods=["GET"])
def get_pending_assignments():
    student_id = request.args.get("student_id")
    assignments = (
        db.session.query(Assignments.title, Assignments.id)
        .join(Courses)
        .join(CourseEnrollments)
        .filter(CourseEnrollments.student_id == student_id)
        .all()
    )
    return jsonify(
        {"pending_assignments": [{"id": a.id, "title": a.title} for a in assignments]}
    )


# 获取已提交作业
@app.route("/api/assignment/submitted", methods=["GET"])
def get_submitted_assignments():
    student_id = request.args.get("student_id")
    submissions = AssignmentSubmissions.query.filter_by(student_id=student_id).all()
    return jsonify(
        {
            "submitted_assignments": [
                {
                    "assignment_id": s.assignment_id,
                    "content": s.content,
                    "file_url": s.file_url,
                }
                for s in submissions
            ]
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
