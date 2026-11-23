#!/bin/bash
# 一键重启前后端服务（调试用）
# 用法：bash restart.sh
# 逻辑：若前后端已在运行则强制杀死，再重新拉起；未运行则直接启动。
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

# 按端口找到并杀死监听进程
kill_port() {
  local port=$1
  local name=$2
  local pids
  pids=$(ss -tlnp 2>/dev/null | grep ":${port} " | grep -oP 'pid=\K[0-9]+' | sort -u || true)
  if [ -n "$pids" ]; then
    echo "  [停止] ${name} (端口 ${port}) PID: $(echo $pids | tr '\n' ' ')"
    for pid in $pids; do
      kill -9 "$pid" 2>/dev/null || true
    done
  else
    echo "  [跳过] ${name} (端口 ${port}) 未运行"
  fi
}

echo "=== 1/3 停止旧进程 ==="
kill_port 8000 "后端"
kill_port 5173 "前端"
# 兜底：按进程特征清理残留
pkill -f "run.py" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

echo ""
echo "=== 2/3 启动后端 ==="
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
  echo "  后端虚拟环境不存在，请先运行 scripts/start-backend.sh 安装依赖"
  exit 1
fi
source .venv/bin/activate
setsid nohup python run.py > "$BACKEND_DIR/backend.log" 2>&1 &
echo "  后端已拉起 PID: $!  (日志: backend/backend.log)"

echo ""
echo "=== 3/3 启动前端 ==="
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  echo "  前端依赖不存在，正在安装..."
  npm install --registry=https://registry.npmmirror.com
fi
setsid nohup npm run dev > "$FRONTEND_DIR/frontend.log" 2>&1 &
echo "  前端已拉起 PID: $!  (日志: frontend/frontend.log)"

echo ""
echo "=== 等待服务就绪 ==="
sleep 4

if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
  echo "  ✓ 后端 http://localhost:8000  (API 文档: /docs)"
else
  echo "  ✗ 后端未就绪，查看 backend/backend.log"
fi

if curl -s -o /dev/null http://localhost:5173 2>&1; then
  echo "  ✓ 前端 http://localhost:5173"
else
  echo "  ✗ 前端未就绪，查看 frontend/frontend.log"
fi

echo ""
echo "完成。实时查看日志："
echo "  tail -f backend/backend.log"
echo "  tail -f frontend/frontend.log"
