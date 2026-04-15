#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "================================================"
echo "  GOROS — goro's 商品聚合門戶"
echo "================================================"

# 后端
echo ""
echo "▶ 启动后端 (FastAPI)..."
cd "$ROOT/backend"
if [ ! -d "venv" ]; then
  echo "  首次运行，创建 Python 虚拟环境..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt -q
else
  source venv/bin/activate
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "  ✓ 后端运行于 http://localhost:8000"

# 前端
echo ""
echo "▶ 启动前端 (Vite)..."
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  echo "  首次运行，安装前端依赖..."
  pnpm install -q
fi

npx vite --port 5173 &
FRONTEND_PID=$!
echo "  ✓ 前端运行于 http://localhost:5173"

echo ""
echo "================================================"
echo "  打开浏览器访问: http://localhost:5173"
echo "  点击右上角「立即同步」按钮开始抓取商品数据"
echo "================================================"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

# 等待 Ctrl+C
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
