""" 数据库模型，要使用则从此引入 """

from datetime import datetime
from database import db


class Users(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.Enum("student", "teacher", "admin", "guest"), nullable=False)
    avatar = db.Column(db.String(255))
    signature = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.Integer, default=1)  # 1:正常 0:禁用


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    teacher_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    category = db.Column(db.String(50))
    status = db.Column(db.Enum("draft", "published", "archived"), default="draft")
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)


class CourseContents(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum("document", "video", "audio", "image"), nullable=False)
    content_url = db.Column(db.String(255))
    sort_order = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)


class PinnedCourses(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    sort_order = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)


class CourseEnrollments(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.Enum("active", "completed", "dropped"), default="active")
    enrolled_at = db.Column(db.TIMESTAMP, default=datetime.now)


class Assignments(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)


class AssignmentSubmissions(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    assignment_id = db.Column(
        db.String(36), db.ForeignKey("assignments.id"), nullable=False
    )
    student_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text)
    file_url = db.Column(db.String(255))
    score = db.Column(db.Numeric(5, 2))
    submitted_at = db.Column(db.TIMESTAMP, default=datetime.now)


class Discussions(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text)
    parent_id = db.Column(db.String(36))
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)


class Notes(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    student_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)


class QuizQuestions(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False)
    creator_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    type = db.Column(
        db.Enum("single", "multiple", "judge", "fill", "essay"), nullable=False
    )
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON)
    answer = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now)


class LearningProgress(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    content_id = db.Column(
        db.String(36), db.ForeignKey("course_contents.id"), nullable=False
    )
    progress = db.Column(db.Numeric(5, 2), default=0)
    last_position = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now, onupdate=datetime.now)


class LoginAttempts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    ip_address = db.Column(db.String(45))
    device_id = db.Column(db.String(255))
    mac_address = db.Column(db.String(17))
    attempt_time = db.Column(db.TIMESTAMP, default=datetime.now)
    is_successful = db.Column(db.Boolean)


class AccountStatus(db.Model):
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), primary_key=True)
    is_locked = db.Column(db.Boolean, default=False)
    lock_reason = db.Column(db.String(100))
    lock_time = db.Column(db.TIMESTAMP)
    unlock_time = db.Column(db.TIMESTAMP)
    failed_attempts = db.Column(db.Integer, default=0)
