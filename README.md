# 日常活动管理系统 (Daily Life System)

一个功能丰富的日常活动管理系统，基于 **FastAPI + Vue 3** 构建，提供现代化 Web 界面，帮助你规划、追踪和管理每日活动、习惯、目标和日志。

## 功能特性

### 📊 仪表盘
- 总活动数、待办、进行中、已完成统计一览
- 完成率展示
- 今日待办和近期活动快速查看
- 今日概览卡片（统计、习惯打卡、目标进度）
- 快捷操作按钮（添加活动、开始番茄钟、写日志）
- 问候语展示

### 📋 活动管理
- 创建、编辑、删除活动，支持标题、描述、优先级（低/中/高/紧急）
- 按分类、状态、优先级筛选活动
- 活动标签（逗号分隔，自由创建）
- 子任务支持（在活动下添加子任务）
- 定时日期和重复规则（每日/每周/每月）
- 重复任务自动生成实例（每日/每周/每月循环）
- 预计时长设置
- 全文搜索（标题、描述、标签）
- 保存常用活动为模板，一键创建

### 📅 日历视图
- 月历展示活动安排
- 支持上月/下月、上年/下年切换
- 一键回到"今天"按钮
- 点击日期查看当天活动详情

### 🕐 时间线视图
- Google Calendar 风格的 24 小时日视图
- 每小时 60px 高度，活动按时间定位为彩色块
- 活动块高度与时长成正比
- 未安排时间的活动单独显示
- 当前时间红色指示线（每分钟更新）
- 日期切换（前一天/后一天/今天）
- 点击活动块查看详情

### 📌 看板视图
- 三列看板：待办 / 进行中 / 已完成
- HTML5 原生拖拽，拖放自动切换状态

### ⚙️ 分类管理
- 自定义活动分类（名称、颜色、图标 emoji）
- 新用户注册自动创建 5 个默认分类（工作/学习/健身/生活/娱乐）
- 侧边栏快速按分类筛选

### 🏷️ 标签管理
- 独立标签管理页面，查看所有标签及使用次数
- 支持重命名、设置颜色、删除标签
- 按标签聚合查看关联活动

### 🎯 习惯追踪
- 创建习惯（名称、描述、频率、目标次数、颜色）
- 30 天打卡日历网格，点击即可打卡/取消
- 火焰数显示累计打卡天数
- 支持删除习惯及所有记录

### 🍅 番茄钟 / 专注计时器
- 大圆形倒计时（可选 15/25/45/60 分钟 + 自定义时长）
- 可关联活动，完成后自动累加时长
- 完成时声音提醒（短提示音/长提示音/旋律，可选）
- 桌面通知提醒
- 休息计时器（专注结束后自动进入休息）
- 跳过休息选项
- 今日专注统计 + 会话历史

### 🎯 目标管理
- 设置周/月/年度目标（标题、目标值、单位）
- 进度条可视化，展开查看进度记录
- 支持添加进度、删除目标

### 📝 每日日志
- 撰写日志：日期、天气、心情、正文内容
- 图片上传：支持上传最多 9 张图片，九宫格展示
- 图片点击放大预览（lightbox）
- 历史日志列表，点击展开/收起内容
- 历史日志评论功能（添加/删除文本评论）
- 搜索框 + 按心情/天气/月份筛选
- Markdown 简易渲染（加粗、斜体、链接、列表）
- 每个日期仅一条日志，重复提交自动更新

### 📈 统计分析
- 分类分布柱状图
- 每周趋势图（近 4 周新增 vs 完成）
- 分类执行时间分析（SVG 饼图，悬停显示详情 tooltip，旋转动画）
- 数据导出：JSON / CSV 格式

### 📄 智能报告（AI Report）
- 日报/周报自动生成
- 活动概览（创建数、完成数、完成率、分类分布）
- 时间分析（专注时长、最高效时段、平均番茄钟时长）
- 习惯总结（坚持情况、连续天数）
- 日志概况（条数、心情趋势）
- 目标进度汇总
- 智能建议（基于数据分析）
- 复制到剪贴板 / 导出为 Markdown 文件

### 🔥 年度热力图 + 月度报告
- GitHub 风格年度热力图（52×7 网格），按年切换
- 月度报告：完成率、最活跃分类、专注时长等

### 🔔 提醒通知
- 活动到期当天自动发送浏览器通知
- 基于 Web Notification API，设置页一键开关

### 🌙 深色模式
- 设置页深色/浅色主题切换
- 全局 CSS 变量覆盖，偏好持久化

### 💾 数据备份与恢复
- 设置页一键导出所有数据为 JSON
- 支持从备份文件导入恢复

### 👥 多用户协作
- 活动分享：输入用户名，选择查看/编辑权限
- 共享活动带标记显示

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

- **后端**: Python 3.8+, FastAPI, Uvicorn, Pydantic
- **前端**: Vue 3 (Composition API + `<script setup>`), Vite, Vue Router 4, Pinia
- **存储**: JSON 文件存储（默认）/ MySQL（设置 `USE_MYSQL=1`）
- **数据库**: pymysql（MySQL 模式）
- **API 文档**: 自动生成 Swagger UI (`/docs`) + ReDoc (`/redoc`)

## 快速开始

### 安装依赖

```bash
# 后端
pip install -r requirements.txt

# 前端（仅开发时需要，构建产物已包含在仓库中）
cd frontend
npm install
```

### 启动服务

```bash
# 默认使用 JSON 文件存储
python3 run_server.py

# 使用 MySQL 存储
USE_MYSQL=1 MYSQL_HOST=localhost MYSQL_USER=root MYSQL_PASSWORD=yourpw MYSQL_DATABASE=daily_life_system python3 run_server.py
```

服务启动后访问 http://localhost:5000

Swagger API 文档：http://localhost:5000/docs

### 前端开发

```bash
cd frontend
npm run dev    # 开发模式（热更新，代理到后端 5000 端口）
npm run build  # 构建到 daily_activity_manager/static/vue/
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `USE_MYSQL` | 是否使用 MySQL（`1`/`true`/`yes`） | 否（使用 JSON 文件） |
| `MYSQL_HOST` | MySQL 主机 | `localhost` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户名 | `root` |
| `MYSQL_PASSWORD` | MySQL 密码 | 空 |
| `MYSQL_DATABASE` | MySQL 数据库名 | `daily_life_system` |
| `SECRET_KEY` | Session 密钥 | 内置默认值 |

## 项目结构

```
DailyLifeSystem/
├── run_server.py                          # 服务入口（Uvicorn）
├── requirements.txt                       # Python 依赖
├── daily_activity_manager/
│   ├── __init__.py
│   ├── api.py                             # FastAPI 主应用（路由注册、静态文件挂载）
│   ├── deps.py                            # 共享依赖（存储实例、认证、限流）
│   ├── schemas.py                         # Pydantic 请求模型（~24 个）
│   ├── models.py                          # 数据模型（Activity, Habit, Goal, PomodoroSession 等）
│   ├── user_model.py                      # 用户模型
│   ├── user_storage.py                    # 用户存储（JSON / MySQL）
│   ├── json_storage.py                    # JSON 文件存储层
│   ├── database.py                        # MySQL 存储层
│   ├── routers/
│   │   ├── auth.py                        # 认证（注册/登录/头像/密码）
│   │   ├── activities.py                  # 活动 CRUD、搜索、日历、子任务
│   │   ├── categories.py                  # 分类 CRUD
│   │   ├── habits.py                      # 习惯 CRUD、打卡
│   │   ├── journals.py                    # 日志 CRUD、图片、评论
│   │   ├── stats.py                       # 统计、热力图、月度报告、导出
│   │   ├── pomodoro.py                    # 番茄钟会话管理
│   │   ├── goals.py                       # 目标 CRUD、进度追踪
│   │   └── backup.py                      # 数据备份与恢复
│   ├── static/vue/                        # Vue 构建输出
│   └── templates/
│       ├── login.html                     # 登录页
│       └── register.html                  # 注册页
├── frontend/
│   ├── vite.config.js                     # Vite 配置
│   ├── package.json
│   └── src/
│       ├── main.js                        # Vue 入口
│       ├── App.vue                        # 根布局
│       ├── style.css                      # 全局样式（含深色模式）
│       ├── api.js                         # API 调用封装
│       ├── i18n.js                        # 中英文国际化
│       ├── router/index.js                # 路由配置（16 个页面）
│       ├── stores/app.js                  # Pinia 状态管理
│       ├── components/
│       │   ├── Sidebar.vue                # 侧边栏导航
│       │   └── ActivityItem.vue           # 活动条目组件
│       └── views/
│           ├── Dashboard.vue              # 仪表盘
│           ├── Activities.vue             # 活动管理
│           ├── Calendar.vue               # 日历视图
│           ├── Kanban.vue                 # 看板视图
│           ├── Categories.vue             # 分类管理
│           ├── Tags.vue                   # 标签管理
│           ├── Habits.vue                 # 习惯追踪
│           ├── Pomodoro.vue               # 番茄钟
│           ├── Goals.vue                  # 目标管理
│           ├── Journal.vue                # 每日日志
│           ├── Heatmap.vue                # 热力图 + 月度报告
│           ├── Templates.vue              # 活动模板
│           ├── Statistics.vue             # 统计分析
│           ├── Timeline.vue              # 时间线视图
│           ├── Report.vue                # 智能报告
│           └── Settings.vue               # 设置
└── uploads/
    ├── avatars/                           # 用户头像
    └── journals/                          # 日志图片
```

## API 接口

### 认证 (`/api/auth`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 注册 |
| POST | `/login` | 密码登录 |
| POST | `/sms/send` | 发送验证码 |
| POST | `/sms/login` | 验证码登录 |
| GET | `/lockout` | 检查锁定状态 |
| POST | `/logout` | 退出 |
| GET | `/me` | 当前用户信息 |
| PUT | `/profile` | 更新资料 |
| POST | `/avatar` | 上传头像 |
| PUT | `/password` | 修改密码 |

### 活动 (`/api/activities`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 列表（支持 status/priority/category_id/today/tags 筛选） |
| POST | `/` | 创建 |
| GET | `/{id}` | 详情 |
| PUT | `/{id}` | 更新 |
| DELETE | `/{id}` | 删除 |
| POST | `/{id}/complete` | 完成 |
| POST | `/{id}/start` | 开始 |
| POST | `/{id}/cancel` | 取消 |
| GET | `/search` | 搜索 |
| GET | `/{id}/subtasks` | 子任务列表 |
| POST | `/{id}/subtasks` | 添加子任务 |
| GET | `/calendar` | 日历数据 |
| GET | `/tags` | 标签列表（含使用次数） |
| PUT | `/tags/{tag}` | 重命名/改色 |
| DELETE | `/tags/{tag}` | 删除标签 |
| POST | `/{id}/share` | 分享活动 |

### 分类 (`/api/categories`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 列表 |
| POST | `/` | 创建 |
| PUT | `/{id}` | 更新 |
| DELETE | `/{id}` | 删除 |

### 习惯 (`/api/habits`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 列表 |
| POST | `/` | 创建 |
| PUT | `/{id}` | 更新 |
| DELETE | `/{id}` | 删除 |
| POST | `/{id}/checkin` | 打卡 |
| POST | `/{id}/uncheckin` | 取消打卡 |
| GET | `/{id}/records` | 记录查询 |

### 番茄钟 (`/api/pomodoro`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/start` | 开始会话 |
| POST | `/{id}/complete` | 完成会话 |
| POST | `/{id}/cancel` | 取消会话 |
| GET | `/sessions` | 会话列表 |
| GET | `/stats` | 专注统计 |

### 目标 (`/api/goals`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 列表 |
| POST | `/` | 创建 |
| PUT | `/{id}` | 更新 |
| DELETE | `/{id}` | 删除 |
| POST | `/{id}/progress` | 添加进度 |
| GET | `/{id}/progress` | 进度列表 |

### 日志 (`/api/journals`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 列表 |
| POST | `/` | 创建/更新（按日期自动 upsert） |
| GET | `/{id}` | 详情 |
| PUT | `/{id}` | 更新 |
| DELETE | `/{id}` | 删除 |
| GET | `/date/{date}` | 按日期查询 |
| GET | `/search` | 搜索日志 |
| POST | `/upload-image` | 上传日志图片 |
| GET | `/{id}/comments` | 评论列表 |
| POST | `/{id}/comments` | 添加评论 |
| DELETE | `/comments/{id}` | 删除评论 |

### 统计与导出 (`/api/stats`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 基础统计 |
| GET | `/detailed` | 详细统计 |
| GET | `/report` | 智能日报/周报生成（?type=daily\|weekly） |
| GET | `/heatmap` | 年度热力图数据 |
| GET | `/monthly-report` | 月度报告 |
| GET | `/export/json` | 导出 JSON |
| GET | `/export/csv` | 导出 CSV |

### 仪表盘 (`/api/dashboard`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 仪表盘聚合数据（统计、习惯、目标、今日活动） |

### 重复任务 (`/api/activities`)
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/generate-recurring` | 自动生成重复任务实例 |

### 模板 (`/api/templates`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 模板列表 |
| POST | `/` | 创建模板 |
| DELETE | `/{id}` | 删除模板 |

### 备份 (`/api/backup`)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/export` | 导出所有数据 |
| POST | `/import` | 导入恢复数据 |

## 许可证

MIT License
