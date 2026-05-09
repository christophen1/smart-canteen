# 校园食堂客流与备餐预测系统

基于 **SpringBoot + Vue + PySpark** 的完整前后端大数据课程设计项目。

## 项目简介

通过校园食堂订单数据，实现在线点餐、后台管理，以及基于 PySpark 的客流分析、高峰时段分析、热门菜品分析和备餐预测。

## 技术栈

| 层 | 技术 |
|-----|------|
| 后端 | Java 17, SpringBoot 3.2, MyBatis Plus 3.5, MySQL 8, JWT |
| 前端 | Vue 3, Element Plus, Axios, Echarts |
| 大数据 | Python 3.10+, PySpark, SparkSQL |
| 构建 | Maven |

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

**方法一：EnvFile 插件（推荐）**

1. `File → Settings → Plugins`，搜索 **EnvFile** 并安装
2. `Run → Edit Configurations`，选中 Spring Boot 启动配置
3. 在 **EnvFile** 标签页，点 `+` → 选择项目根目录的 `.env` 文件
4. 勾选 **Enable EnvFile**

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

### 6. 运行 API 测试

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
