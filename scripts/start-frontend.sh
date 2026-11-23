#!/bin/bash
# 启动前端开发服务
set -e
cd "$(dirname "$0")/../frontend"

if [ ! -d "node_modules" ]; then
  echo "安装前端依赖..."
  npm install
fi

echo "启动前端开发服务 http://0.0.0.0:5173"
exec npm run dev
