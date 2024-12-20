# database.py
"""
若要在后端使用 mysql 数据库内容，请从该文件引入 db 对象
若要修改数据库的配置，请修改根目录中 .env 文件的内容
"""
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 创建数据库对象
db = SQLAlchemy(app)
