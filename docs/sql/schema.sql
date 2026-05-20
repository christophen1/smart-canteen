-- ============================================
-- Smart Canteen 数据库建表脚本
-- 数据库名: smart_canteen
-- ============================================

CREATE DATABASE IF NOT EXISTS smart_canteen
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE smart_canteen;

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（BCrypt加密）',
    real_name VARCHAR(50) DEFAULT '' COMMENT '真实姓名',
    phone VARCHAR(20) DEFAULT '' COMMENT '手机号',
    role TINYINT DEFAULT 0 COMMENT '角色：0=普通用户, 1=管理员',
    status TINYINT DEFAULT 1 COMMENT '状态：0=禁用, 1=正常',
    is_deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================
-- 2. 分类表
-- ============================================
CREATE TABLE IF NOT EXISTS category (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    name VARCHAR(50) NOT NULL COMMENT '分类名称',
    sort INT DEFAULT 0 COMMENT '排序值',
    is_deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品分类表';

-- ============================================
-- 3. 菜品表
-- ============================================
CREATE TABLE IF NOT EXISTS dish (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    category_id BIGINT NOT NULL COMMENT '分类ID',
    name VARCHAR(100) NOT NULL COMMENT '菜品名称',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    image VARCHAR(255) DEFAULT '' COMMENT '图片路径',
    description VARCHAR(500) DEFAULT '' COMMENT '菜品描述',
    status TINYINT DEFAULT 1 COMMENT '状态：0=下架, 1=上架',
    is_deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category_id (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品表';

-- ============================================
-- 4. 订单表
-- ============================================
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_no VARCHAR(32) NOT NULL COMMENT '订单号',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    total_amount DECIMAL(10,2) NOT NULL COMMENT '订单总金额',
    status TINYINT DEFAULT 1 COMMENT '状态：0=已取消, 1=待支付, 2=已支付, 3=已完成',
    remark VARCHAR(255) DEFAULT '' COMMENT '备注',
    is_deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_order_no (order_no),
    INDEX idx_user_id (user_id),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- ============================================
-- 5. 订单明细表
-- ============================================
CREATE TABLE IF NOT EXISTS order_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    order_id BIGINT NOT NULL COMMENT '订单ID',
    dish_id BIGINT NOT NULL COMMENT '菜品ID',
    dish_name VARCHAR(100) NOT NULL COMMENT '菜品名（快照）',
    dish_price DECIMAL(10,2) NOT NULL COMMENT '单价（快照）',
    quantity INT NOT NULL COMMENT '数量',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- ============================================
-- 6. 高峰时段分析结果表
-- ============================================
CREATE TABLE IF NOT EXISTS peak_hour_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    analysis_date DATE NOT NULL COMMENT '分析运行日期',
    hour INT NOT NULL COMMENT '小时（0-23）',
    order_count DECIMAL(10,2) DEFAULT 0 COMMENT '日均订单数',
    total_amount DECIMAL(10,2) DEFAULT 0 COMMENT '日均销售额',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_date (analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='高峰时段分析结果表';

-- ============================================
-- 7. 菜品销量分析结果表
-- ============================================
CREATE TABLE IF NOT EXISTS dish_sales_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    analysis_date DATE NOT NULL COMMENT '分析运行日期',
    dish_id BIGINT NOT NULL COMMENT '菜品ID',
    dish_name VARCHAR(100) NOT NULL COMMENT '菜品名',
    sales_count DECIMAL(10,2) DEFAULT 0 COMMENT '日均销量',
    sales_amount DECIMAL(10,2) DEFAULT 0 COMMENT '日均销售额',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_analysis_date (analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品销量分析结果表';

-- ============================================
-- 8. 客流分析结果表
-- ============================================
CREATE TABLE IF NOT EXISTS customer_flow_analysis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    analysis_date DATE NOT NULL COMMENT '分析日期',
    daily_orders INT DEFAULT 0 COMMENT '日订单量',
    daily_amount DECIMAL(10,2) DEFAULT 0 COMMENT '日总销售额',
    avg_order_amount DECIMAL(10,2) DEFAULT 0 COMMENT '客单价',
    total_users INT DEFAULT 0 COMMENT '消费用户数',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_analysis_date (analysis_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='客流分析结果表';

-- ============================================
-- 9. 备餐预测结果表
-- ============================================
CREATE TABLE IF NOT EXISTS meal_prediction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    predict_date DATE NOT NULL COMMENT '预测日期',
    dish_id BIGINT NOT NULL COMMENT '菜品ID',
    dish_name VARCHAR(100) NOT NULL COMMENT '菜品名',
    predicted_sales INT DEFAULT 0 COMMENT '预测销量',
    suggested_prepare INT DEFAULT 0 COMMENT '建议备餐量',
    confidence DECIMAL(5,4) DEFAULT 0 COMMENT '预测置信度',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_predict_date (predict_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='备餐预测结果表';
