# redrock-task1

任务一：用 `uv` 管理 Python 环境，编写一个**异步并发**请求多个 HTTP 接口并把结果汇总的脚本。

## 环境要求
- Python 3.11+
- uv
- Git

## 快速开始

```bash
uv sync                                              # 按 uv.lock 安装依赖
uv run python fetch_many.py --timeout 30             # 请求内置 3 个示例接口