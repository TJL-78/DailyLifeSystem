# 日常活动管理系统 (Daily Life System)

一个基于 Python 的日常活动管理系统，帮助你规划、追踪和管理每日活动。

## 功能

- 创建、查询、更新、删除活动
- 按状态、优先级、分类筛选
- 支持定时日期和重复规则（每日/每周/每月）
- 活动统计
- 命令行界面

## 使用方法

```bash
# 添加活动
python3 -m daily_activity_manager.cli add "晨跑" -p high --date 2026-05-08 --time 07:00 -c "健身"

# 列出所有活动
python3 -m daily_activity_manager.cli list

# 列出今日活动
python3 -m daily_activity_manager.cli list --today

# 完成活动
python3 -m daily_activity_manager.cli complete <activity-id>

# 查看统计
python3 -m daily_activity_manager.cli stats
```

## 项目结构

```
daily_activity_manager/
├── __init__.py    # 包初始化
├── models.py      # 数据模型（Activity, 状态, 优先级等）
├── storage.py     # JSON 文件存储层
├── manager.py     # 业务逻辑管理器
└── cli.py         # 命令行界面
```
