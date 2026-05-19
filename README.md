# 校园食堂客流与备餐预测系统

基于 **SpringBoot + Vue + PySpark** 的完整前后端大数据课程设计项目。

## 项目简介

通过校园食堂订单数据，实现在线点餐、后台管理，以及基于 PySpark 的客流分析、高峰时段分析、热门菜品分析和备餐预测。

## 技术栈

| 层 | 技术 |
|-----|------|
| 后端 | Java 17, SpringBoot 3.2, MyBatis Plus 3.5, MySQL 8, JWT |
| 前端 | Vue 3, Vite, Element Plus, Vue Router, Axios, Echarts |
| 大数据 | Python 3.10+, PySpark, SparkSQL |
| 构建 | Maven (后端), npm (前端) |

## 项目结构

```
smart-canteen/
├── springboot-backend/     # SpringBoot 后端（Java）
├── pyspark-analysis/       # PySpark 离线分析（Python）
├── vue-frontend/           # Vue 前端
├── scripts/                # 脚本
│   └── test_api.py         # API 测试脚本
├── docs/                   # 文档
│   ├── PRD.md              # 产品需求文档
│   ├── sql/schema.sql      # 建表脚本
│   └── report/             # 大作业报告
└── README.md
```

## 快速开始

### 1. 环境要求

- JDK 17
- Maven 3.8+
- MySQL 8.0
- Node.js 18+（前端开发用）
- Python 3.10+（PySpark 分析用）

### 2. 数据库

```bash
# 在 MySQL 中执行建表脚本
mysql -u root -p < docs/sql/schema.sql
```

### 3. 生成测试数据

```bash
python scripts/generate_data.py     # 生成 data.sql
mysql -u root -p < scripts/data.sql # 导入数据
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入 MySQL 密码和 JWT Secret
```

#### 在 IntelliJ IDEA 中加载 .env

**方法一：直接用IDEA配置**

1. IDEA 右上角直接点击 `Edit Configurations`
2. 点击修改选项，勾选 `环境变量`
3. `环境变量` 标签选中.env文件
4. 确定


**方法二：手动填入 Environment variables**

1. `Run → Edit Configurations`，选中 Spring Boot 启动配置
2. 在 **Environment variables** 输入框里粘贴（格式：`KEY=VALUE;KEY2=VALUE2`）：

```
DB_PASSWORD=你的密码;JWT_SECRET=随便写一串英文
```

### 5. 启动后端

```bash
cd springboot-backend
mvn spring-boot:run
```

### 6. 运行 PySpark 分析

```bash
# 安装 Python 依赖
pip install -r pyspark-analysis/requirements.txt

# 执行分析（确保 MySQL 中有订单数据）
python pyspark-analysis/main.py
```

PySpark 会读取 MySQL 中的订单数据，依次执行客流分析、高峰时段分析、菜品销量分析和备餐预测，结果写回 MySQL 分析结果表，前端数据看板可直接查询展示。

> **Windows 注意**：PySpark 需要 Java 8/11 环境，配置细节见 `docs/report/chapter3-implementation.md` 3.1.3 节。

### 7. 启动前端

```bash
cd vue-frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，通过 Vite proxy 将 `/api` 请求转发到后端 `localhost:8080`。

启动后访问：
- 用户端：`http://localhost:5173/home`
- 管理端：`http://localhost:5173/admin/login`

### 8. 运行 API 测试

```bash
pip install requests
python scripts/test_api.py
```

## 文档

- [产品需求文档](docs/PRD.md)
- [大作业报告](docs/report/)
- [建表脚本](docs/sql/schema.sql)

## 小组协作说明

- `.env` 文件包含敏感信息，已加入 `.gitignore`，不提交
- `.env.example` 为模板文件，组员复制后填入自己的配置
