import os
from dotenv import load_dotenv

# 从 .env 文件加载环境变量
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '3306'),
    'database': os.getenv('DB_NAME', 'smart_canteen'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# PySpark JDBC 连接 URL
JDBC_URL = f"jdbc:mysql://{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?useSSL=false&serverTimezone=UTC"

# JDBC 连接属性
JDBC_PROPERTIES = {
    "user": DB_CONFIG['user'],
    "password": DB_CONFIG['password'],
    "driver": "com.mysql.cj.jdbc.Driver"
}

# MySQL Connector/J JAR 文件路径（JAR 已存在于 lib 目录）
MYSQL_JAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib/mysql-connector-j-9.7.0.jar")
