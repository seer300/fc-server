#!/bin/bash
# 启动后端服务
set -e
cd "$(dirname "$0")/../backend"

if [ ! -d ".venv" ]; then
  echo "创建 Python 虚拟环境..."
  python3 -m venv .venv
fi

source .venv/bin/activate
echo "安装依赖..."
pip install -q -r requirements.txt

echo "启动后端服务 http://0.0.0.0:8000"
exec python run.py
