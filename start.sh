#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "================================================"
echo "  GOROS — goro's 商品聚合門戶"
echo "================================================"

# Set default environment if not set
export APP_ENV=${APP_ENV:-development}
export ALLOW_MANUAL_SYNC=${ALLOW_MANUAL_SYNC:-true}

echo "環境: $APP_ENV (同步按鈕: $([ "$ALLOW_MANUAL_SYNC" = "true" ] && echo "顯示" || echo "隱藏"))"
echo ""

# 后端
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

# 檢查是否存在 .env 文件，若無則從範例創建
if [ ! -f ".env" ]; then
  echo "  正在創建默認 .env 檔案..."
  cp .env.example .env 2>/dev/null || echo "WARNING: 找不到 .env.example，請手動創建 .env 檔案"
fi

# 使用正確的環境變量啟動前端
if [ "$APP_ENV" = "production" ]; then
  echo "  使用生產模式啟動..."
  npx vite --port 5173 --mode production &
else
  echo "  使用開發模式啟動..."
  npx vite --port 5173 &
fi

FRONTEND_PID=$!
echo "  ✓ 前端运行于 http://localhost:5173"

echo ""
echo "================================================"
echo "  打开浏览器访问: http://localhost:5173"
echo "  當前環境: $APP_ENV"
echo "  同步按鈕: $([ "$ALLOW_MANUAL_SYNC" = "true" ] && echo "顯示" || echo "已隱藏")"
echo "================================================"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo ""

# 等待 Ctrl+C
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
