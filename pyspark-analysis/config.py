import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '3306'),
    'database': os.getenv('DB_NAME', 'smart_canteen'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# JDBC URL for PySpark
JDBC_URL = f"jdbc:mysql://{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?useSSL=false&serverTimezone=UTC"

# JDBC properties
JDBC_PROPERTIES = {
    "user": DB_CONFIG['user'],
    "password": DB_CONFIG['password'],
    "driver": "com.mysql.cj.jdbc.Driver"
}

# Path to MySQL Connector/J JAR (adjust path as needed)
MYSQL_JAR_PATH = "lib/mysql-connector-j-9.7.0.jar"  # JAR is already present