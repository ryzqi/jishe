# 物流配送管理系统

## 项目介绍

物流配送管理系统是一个基于FastAPI和PostgreSQL的现代化物流管理解决方案，适用于仓库管理、物流调度和配送跟踪。

## 特性

- 基于FastAPI的高性能API接口
- PostgreSQL数据库支持
- 异步操作支持
- 基于OAuth2.0的JWT认证
- 用户角色权限管理
- 仓库和库存管理
- 物流配送追踪
- 无人机任务调度
- 巡检任务管理

## 环境要求

- Python 3.11+
- PostgreSQL 13+
- Redis (可选，用于缓存和队列)

## 安装

1. 克隆仓库

```bash
git clone <repository-url>
cd logistics-management
```

2. 使用Poetry安装依赖

```bash
poetry install
```

3. 设置环境变量

复制示例环境文件并根据需要修改：

```bash
cp .env.example .env
```

4. 运行数据库迁移

```bash
poetry run alembic upgrade head
```

5. 初始化系统和创建管理员账户

Windows:

```bash
create_admin.bat
```

Linux/macOS:

```bash
python -m app.scripts.initialize_system
```

初始化后，将创建以下角色和用户:

- 角色: 超级管理员(role_id=1)、运输管理员(role_id=2)、仓库管理员(role_id=3)
- 超级管理员账户: admin / 123456

6. 启动开发服务器

```bash
poetry run python -m app.main
```

或使用Uvicorn：

```bash
poetry run uvicorn app.main:app --reload
```

## API文档

启动应用后，可以通过以下URL访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 认证和授权系统

系统使用OAuth2.0认证机制，基于JWT令牌实现。支持多种角色并实现了基于角色的访问控制（RBAC）。

### 角色设计

系统设计了3种不同的角色，每个角色拥有不同的权限：

1. **超级管理员** (role_id=1): 拥有系统全部功能的访问权限
2. **运输管理员** (role_id=2): 拥有物流配送、无人机任务和巡检任务相关的权限
3. **仓库管理员** (role_id=3): 拥有仓库和库存管理相关的权限

角色权限采用了最小权限原则，每个角色只能访问其职责范围内的功能。

### 登录获取令牌

```http
POST /api/v1/auth/login
```

请求体：

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

响应：

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 使用令牌访问受保护资源

在请求头中包含令牌：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 获取当前用户信息

```http
GET /api/v1/users/me
```

响应：

```json
{
  "id": 1,
  "username": "admin"
}
```

### 获取当前用户角色

```http
GET /api/v1/users/me/roles
```

响应：

```json
[
  {
    "role_id": 1,
    "role_name": "超级管理员"
  }
]
```

### 角色权限划分

| 角色       | 可访问功能                     |
| ---------- | ------------------------------ |
| 超级管理员 | 所有功能                       |
| 运输管理员 | 无人机管理、巡检任务、物流配送 |
| 仓库管理员 | 仓库管理、库存管理             |

### 用户注册

当前系统不提供公开注册功能，用户由超级管理员创建。

```http
POST /api/v1/users
```

请求体：

```json
{
  "username": "new_user",
  "password": "secure_password",
  "role_ids": [2]
}
```

## 项目架构

系统采用分层架构设计，遵循关注点分离原则：

1. **表示层（API层）** - 处理HTTP请求和响应
2. **服务层（Service层）** - 实现业务逻辑
3. **数据访问层（CRUD层）** - 提供数据库访问操作
4. **模型层（Model层）** - 定义数据库模型
5. **模式层（Schema层）** - 定义数据验证模式

## 项目结构

```
app/
├── api/            # API路由
│   └── v1/         # API v1版本
├── core/           # 核心功能
│   ├── config.py   # 配置
│   ├── context.py  # 应用上下文管理
│   └── security.py # 安全工具
├── crud/           # 数据库CRUD操作
├── db/             # 数据库设置
├── models/         # 数据库模型
├── schemas/        # Pydantic模型
├── scripts/        # 管理脚本
│   ├── create_admin.py       # 创建管理员脚本
│   ├── create_roles.py       # 创建角色脚本
│   └── initialize_system.py  # 系统初始化脚本
├── services/       # 业务逻辑层
├── utils/          # 工具函数
└── main.py         # 应用入口
```

## 最佳实践

本项目遵循以下FastAPI最佳实践：

1. **使用上下文管理器代替事件钩子** - 更好地管理应用生命周期
2. **关注点分离** - 严格区分不同层次的职责
3. **依赖注入** - 使用FastAPI依赖注入系统管理资源
4. **全异步操作** - 提高并发性能
5. **统一错误处理** - 使用HTTPException和统一错误响应模型
6. **角色权限控制** - 使用基于角色的访问控制系统

## 数据模型 (Data Models)

系统使用SQLAlchemy 2.0作为ORM，针对PostgreSQL数据库进行设计。模型分为两部分：

### SQLAlchemy ORM 模型 (`app/models/`)

所有模型都继承自 `app/db/base.py`中的 `Base`类，自动包含id、created_at和updated_at字段。

- **Drone** (`app/models/drone.py`): 无人机模型

  - `id`: 无人机编号
  - `drone_type`: 机型
  - `states`: 无人机状态：1->正常工作，0->未工作
- **Error** (`app/models/error.py`): 问题模型

  - `error_id`: 问题编号
  - `error_content`: 问题内容
  - `error_found_time`: 问题发现时间
  - `states`: 问题状态：0->待解决，1->正在解决
- **Goods** (`app/models/goods.py`): 货物模型

  - `id`: 货物种类唯一标识
  - `goods_name`: 货物种类名称
- **Patrol** (`app/models/patrol.py`): 巡查记录模型

  - `id`: 巡查记录唯一标识
  - `drone_id`: 无人机编号
  - `address`: 在寻路段
  - `predict_fly_time`: 预计飞行时长
  - `fly_start_datetime`: 开始飞行时间
- **Role** (`app/models/role.py`): 角色模型

  - `role_id`: 角色唯一标识
  - `role_name`: 角色名称
- **Warehouse** (`app/models/warehouse.py`): 仓库模型

  - `id`: 仓库唯一标识
  - `warehouse_name`: 仓库名称
  - `states`: 仓库状态
- **Stock** (`app/models/stock.py`): 库存模型

  - `id`: 库存唯一标识
  - `warehouse_id`: 仓库唯一标识
  - `goods_id`: 货物种类唯一标识
  - `all_count`: 总库存量
  - `last_add_count`: 新增库存量
  - `last_add_date`: 新增库存时间
- **User** (`app/models/user.py`): 用户模型

  - `id`: 用户唯一标识
  - `username`: 用户名
  - `password`: 用户密码
- **UserRole** (`app/models/user_role.py`): 用户角色关联模型

  - `user_id`: 用户唯一标识
  - `role_id`: 角色唯一标识

### Pydantic Schema 模型 (`app/schemas/`)

每个数据模型都有对应的Pydantic模型，用于API输入验证和响应生成：

- **创建模型**（如 `DroneCreate`）: 用于创建资源的请求体验证
- **更新模型**（如 `DroneUpdate`）: 用于更新资源的请求体验证，所有字段都是可选的
- **响应模型**（如 `DroneResponse`）: 用于API响应的序列化

## 关系映射

系统中的主要关系包括：

- **Drone - Patrol**: 一对多（一个无人机可以有多个巡查记录）
- **Warehouse - Stock**: 一对多（一个仓库可以有多个库存记录）
- **Goods - Stock**: 一对多（一种货物可以在多个仓库有库存）
- **User - Role**: 多对多（通过UserRole关联表）
