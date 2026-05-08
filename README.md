# 日常活动管理系统 (Daily Life System)

一个功能丰富的日常活动管理系统，基于 Python Flask 构建，提供 Web 界面，帮助你规划、追踪和管理每日活动、习惯和日志。

## 功能特性

### 📊 仪表盘
- 总活动数、待办、进行中、已完成统计一览
- 完成率展示
- 今日待办和近期活动快速查看

### 📋 活动管理
- 创建、编辑、删除活动，支持标题、描述、优先级（低/中/高/紧急）
- 按分类、状态、优先级筛选活动
- 活动标签（逗号分隔，自由创建）
- 子任务支持（在活动下添加子任务）
- 定时日期和重复规则（每日/每周/每月）
- 预计时长设置
- 全文搜索（标题、描述、标签）

### 📅 日历视图
- 月历展示活动安排
- 支持上月/下月、上年/下年切换
- 一键回到"今天"按钮
- 点击日期查看当天活动详情

### ⚙️ 分类管理
- 自定义活动分类（名称、颜色、图标 emoji）
- 新用户注册自动创建 5 个默认分类（工作/学习/健身/生活/娱乐）
- 侧边栏快速按分类筛选

### 🎯 习惯追踪
- 创建习惯（名称、描述、频率、目标次数、颜色）
- 30 天打卡日历网格，点击即可打卡/取消
- 火焰数显示累计打卡天数
- 支持删除习惯及所有记录

### 📝 每日日志
- 撰写日志：日期、天气、心情、正文内容
- 图片上传：支持上传最多 9 张图片，朋友圈风格九宫格展示
- 图片点击放大预览（lightbox）
- 一键清空表单功能
- 历史日志列表，点击展开/收起内容
- 历史日志评论功能（添加/删除文本评论）
- 每个日期仅一条日志，重复提交自动更新

### 📈 统计分析
- 分类分布柱状图
- 每周趋势图（近 4 周新增 vs 完成）
- 分类执行时间分析（SVG 饼图，鼠标悬停查看详情）
- 数据导出：JSON / CSV 格式

### 👤 个人设置
- 头像上传（支持 multipart 文件上传和 base64）
- 个人资料编辑（显示名称、邮箱、手机号）
- 修改密码
- 中英文语言切换（localStorage 持久化）

### 🔐 登录与安全
- 用户名/密码登录
- 手机号 + 短信验证码登录（模拟，验证码输出到服务器控制台）
- 注册新账号
- 登录失败 3 次后锁定 60 秒（按 IP 追踪）

## 技术栈

- **后端**: Python 3.8+, Flask
- **前端**: 单文件 SPA (HTML/CSS/JavaScript)，无第三方前端框架
- **存储**: JSON 文件存储（默认）/ MySQL（设置 `USE_MYSQL=1`）
- **数据库**: pymysql（MySQL 模式）

## 快速开始

### 安装依赖

```bash
pip install flask pymysql
```

### 启动服务

```bash
# 默认使用 JSON 文件存储
python3 run_server.py

# 使用 MySQL 存储
USE_MYSQL=1 MYSQL_HOST=localhost MYSQL_USER=root MYSQL_PASSWORD=yourpw MYSQL_DATABASE=daily_life_system python3 run_server.py
```

服务启动后访问 http://localhost:5000

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `USE_MYSQL` | 是否使用 MySQL（`1`/`true`/`yes`） | 否（使用 JSON 文件） |
| `MYSQL_HOST` | MySQL 主机 | `localhost` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户名 | `root` |
| `MYSQL_PASSWORD` | MySQL 密码 | 空 |
| `MYSQL_DATABASE` | MySQL 数据库名 | `daily_life_system` |
| `SECRET_KEY` | Flask session 密钥 | 内置默认值 |

## 项目结构

```
DailyLifeSystem/
├── run_server.py                          # 服务入口
├── daily_activity_manager/
│   ├── __init__.py                        # 包初始化
│   ├── api.py                             # Flask Web API（所有路由）
│   ├── models.py                          # 数据模型（Activity, Category, Habit, Journal, JournalComment）
│   ├── user_model.py                      # 用户模型（密码哈希、头像、手机号）
│   ├── user_storage.py                    # 用户存储（JSON / MySQL）
│   ├── json_storage.py                    # JSON 文件存储层
│   ├── database.py                        # MySQL 存储层
│   └── templates/
│       ├── index.html                     # 主页面 SPA（含所有页面和 i18n）
│       ├── login.html                     # 登录页（密码/短信双模式）
│       └── register.html                  # 注册页
├── uploads/
│   ├── avatars/                           # 用户头像
│   └── journals/                          # 日志图片
└── .gitignore
```

## API 接口

### 认证
- `POST /api/auth/register` — 注册
- `POST /api/auth/login` — 密码登录
- `POST /api/auth/sms/send` — 发送验证码
- `POST /api/auth/sms/login` — 验证码登录
- `GET /api/auth/lockout` — 检查锁定状态
- `POST /api/auth/logout` — 退出
- `GET /api/auth/me` — 当前用户信息
- `PUT /api/auth/profile` — 更新资料
- `POST /api/auth/avatar` — 上传头像
- `PUT /api/auth/password` — 修改密码

### 活动
- `GET /api/activities` — 列表（支持 status/priority/category_id/today 筛选）
- `POST /api/activities` — 创建
- `GET /api/activities/<id>` — 详情
- `PUT /api/activities/<id>` — 更新
- `DELETE /api/activities/<id>` — 删除
- `POST /api/activities/<id>/complete` — 完成
- `POST /api/activities/<id>/start` — 开始
- `POST /api/activities/<id>/cancel` — 取消
- `GET /api/activities/search?q=` — 搜索
- `GET /api/activities/<id>/subtasks` — 子任务列表
- `POST /api/activities/<id>/subtasks` — 添加子任务
- `GET /api/activities/calendar?start=&end=` — 日历数据

### 分类
- `GET /api/categories` — 列表
- `POST /api/categories` — 创建
- `PUT /api/categories/<id>` — 更新
- `DELETE /api/categories/<id>` — 删除

### 习惯
- `GET /api/habits` — 列表
- `POST /api/habits` — 创建
- `PUT /api/habits/<id>` — 更新
- `DELETE /api/habits/<id>` — 删除
- `POST /api/habits/<id>/checkin` — 打卡
- `POST /api/habits/<id>/uncheckin` — 取消打卡
- `GET /api/habits/<id>/records` — 记录查询

### 日志
- `GET /api/journals` — 列表
- `POST /api/journals` — 创建/更新（按日期自动 upsert）
- `GET /api/journals/<id>` — 详情
- `PUT /api/journals/<id>` — 更新
- `DELETE /api/journals/<id>` — 删除
- `GET /api/journals/date/<date>` — 按日期查询
- `POST /api/journals/upload-image` — 上传日志图片
- `GET /api/journals/<id>/comments` — 评论列表
- `POST /api/journals/<id>/comments` — 添加评论
- `DELETE /api/journals/comments/<id>` — 删除评论

### 统计与导出
- `GET /api/stats` — 基础统计
- `GET /api/stats/detailed` — 详细统计（分类分布、周趋势、时间分析）
- `GET /api/export/json` — 导出 JSON
- `GET /api/export/csv` — 导出 CSV

## 许可证

MIT License
