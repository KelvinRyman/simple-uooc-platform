from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import uuid
import random
import string
from datetime import datetime, timedelta
import requests
from flask_cors import CORS
from functools import wraps
from database import db, app
from model import Users, LoginAttempts
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)

# 加载环境变量
load_dotenv()

# CORS配置
CORS(app, resources={r"/api/*": {"origins": "*"}})

# JWT配置
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

bcrypt = Bcrypt(app)

RECAPTCHA_SECRET_KEY = (
    "6Ld1LqEqAAAAANIMwASgAZpRTbByjGPE1W6kEB7x"  # 从环境变量获取，用于验证reCAPTCHA
)

# 黑名单集合，用于存储失效的token
jwt_blocklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in jwt_blocklist


def generate_guest_username():
    # 生成随机6位字符串
    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"guest-{random_suffix}"


# 验证reCAPTCHA
def verify_recaptcha(token):
    if not token:
        return False
    try:
        response = requests.post(
            "https://www.recaptcha.net/recaptcha/api/siteverify",
            {"secret": RECAPTCHA_SECRET_KEY, "response": token},
        )
        result = response.json()
        return result.get("success", False)
    except:
        return False


@app.route("/api/login", methods=["POST"])
def user_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user_type = data.get("userType")
    recaptcha_token = data.get("recaptchaToken")

    try:
        # 检查登录失败次数
        ip_address = request.remote_addr
        failed_attempts = LoginAttempts.query.filter(
            LoginAttempts.ip_address == ip_address,
            LoginAttempts.is_successful == False,
            LoginAttempts.attempt_time >= datetime.now() - timedelta(hours=1),
        ).count()

        if failed_attempts >= 3:
            if not verify_recaptcha(recaptcha_token):
                return jsonify({"success": False, "message": "请完成人机验证"})

        role_map = {"1": "student", "2": "teacher", "3": "admin"}
        user = Users.query.filter_by(
            username=username, role=role_map.get(user_type)
        ).first()

        if not user:
            return jsonify({"success": False, "message": "用户名或用户类型错误"})

        if user.status == 0:
            return jsonify({"success": False, "message": "账号已被禁用"})

        if not bcrypt.check_password_hash(user.password, password):
            login_attempt = LoginAttempts(
                user_id=user.id, ip_address=request.remote_addr, is_successful=False
            )
            db.session.add(login_attempt)
            db.session.commit()
            return jsonify({"success": False, "message": "密码错误"})

        # 生成Token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role, "username": user.username},
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={"role": user.role, "username": user.username},
        )

        # 记录登录成功
        login_attempt = LoginAttempts(
            user_id=user.id, ip_address=request.remote_addr, is_successful=True
        )
        db.session.add(login_attempt)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "登录成功",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"id": user.id, "username": user.username, "role": user.role},
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"})


@app.route("/api/register", methods=["POST"])
def user_register():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")
        email = data.get("email")

        # 验证必填字段
        if not all([username, password, role]):
            return jsonify({"success": False, "message": "缺少必要的注册信息"}), 400

        # 验证用户类型是否合法
        role_map = {"1": "student", "2": "teacher", "3": "admin"}
        if role not in role_map:
            return jsonify({"success": False, "message": "无效的用户类型"}), 400

        # 检查用户名是否已存在
        if Users.query.filter_by(username=username).first():
            return jsonify({"success": False, "message": "用户名已被注册"}), 409

        # 创建新用户
        new_user = Users(
            id=str(uuid.uuid4()),
            username=username,
            password=bcrypt.generate_password_hash(password).decode("utf-8"),
            role=role_map[role],
            avatar="../assets/sys_img/default_avatar.svg",
            status=1,
        )

        db.session.add(new_user)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "注册成功",
                    "user": {
                        "id": new_user.id,
                        "username": new_user.username,
                        "role": new_user.role,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"注册错误: {str(e)}")
        return jsonify({"success": False, "message": "注册失败，请稍后重试"}), 500


@app.route("/api/guest/login", methods=["POST"])
def guest_login():
    try:
        # 生成游客信息
        user_id = str(uuid.uuid4())
        guest_username = generate_guest_username()

        while Users.query.filter_by(username=guest_username).first():
            guest_username = generate_guest_username()

        new_guest = Users(
            id=user_id,
            username=guest_username,
            password=bcrypt.generate_password_hash("guest").decode("utf-8"),
            role="guest",
            avatar="../assets/sys_img/default_avatar.svg",
            status=1,
        )

        db.session.add(new_guest)
        db.session.commit()

        # 生成游客token
        access_token = create_access_token(
            identity=user_id,
            additional_claims={"role": "guest", "username": guest_username},
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            additional_claims={"role": "guest", "username": guest_username},
        )

        return jsonify(
            {
                "success": True,
                "message": "游客登录成功",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user_id,
                    "username": guest_username,
                    "role": "guest",
                    "avatar": "../assets/sys_img/default_avatar.svg",
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"游客登录错误: {str(e)}")
        return jsonify({"success": False, "message": "游客登录失败，请稍后重试"}), 500


@app.route("/api/guest/logout", methods=["POST"])
@jwt_required()
def guest_logout():
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(Users, current_user_id)  # 修改这里

        if user and user.role == "guest":
            # 删除登录记录
            LoginAttempts.query.filter_by(user_id=current_user_id).delete()
            # 删除游客用户
            db.session.delete(user)
            db.session.commit()

            # 将token加入黑名单
            jti = get_jwt()["jti"]
            jwt_blocklist.add(jti)

            return jsonify({"success": True, "message": "游客账号已注销"})
        else:
            return (
                jsonify({"success": False, "message": "非游客账号，无法执行此操作"}),
                403,
            )

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"游客注销错误: {str(e)}")
        return jsonify({"success": False, "message": "注销失败，请稍后重试"}), 500


def get_user_permissions(role):
    """获取用户角色对应的权限列表"""
    base_permissions = {"canViewProfile": True, "canViewCourses": True}

    role_permissions = {
        "student": {
            **base_permissions,
            "canSubmitAssignments": True,
            "canViewGrades": True,
            "canCreateNotes": True,
        },
        "teacher": {
            **base_permissions,
            "canCreateCourse": True,
            "canGradeAssignments": True,
            "canManageCourseContent": True,
        },
        "admin": {
            **base_permissions,
            "canManageUsers": True,
            "canManageAllCourses": True,
            "canViewSystemLogs": True,
        },
        "guest": {
            "canViewCourses": True,
            "canRegister": True,
            "canViewPublicContent": True,
        },
    }

    return role_permissions.get(role, {})


@app.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        jwt_blocklist.add(jti)
        return jsonify({"success": True, "message": "已成功退出登录"})
    except Exception as e:
        return jsonify({"success": False, "message": f"登出失败: {str(e)}"}), 500


@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    current_user = db.session.get(Users, identity)  # 修改这里
    if not current_user:
        return jsonify({"success": False, "message": "用户不存在"}), 404

    access_token = create_access_token(
        identity=identity,
        additional_claims={
            "role": current_user.role,
            "username": current_user.username,
        },
    )
    return jsonify({"success": True, "access_token": access_token})


if __name__ == "__main__":
    app.run(debug=True)
