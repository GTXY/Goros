#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR"

echo "🔍 Goros 服務狀態檢查"
echo "======================"
echo ""

# 檢查後端
echo "後端服務 (FastAPI - 端口 8000):"
if curl -s -f http://localhost:8000/api/products/stats > /dev/null; then
    echo "  ✅ 運行中"
    # 獲取一些統計信息
    STATS=$(curl -s http://localhost:8000/api/products/stats)
    TOTAL=$(echo $STATS | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_products', 0))")
    AVAILABLE=$(echo $STATS | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('available_products', 0))")
    SOURCE_COUNT=$(echo $STATS | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('sources', [])))")
    echo "  📊 總商品: $TOTAL"
    echo "  📦 有貨商品: $AVAILABLE"
    echo "  🏪 數據源數量: $SOURCE_COUNT"
else
    echo "  ❌ 未運行"
fi

echo ""

# 檢查前端
echo "前端服務 (Vite - 端口 5173):"
if curl -s -f http://localhost:5173 > /dev/null; then
    echo "  ✅ 運行中"
    echo "  🌐 訪問地址: http://localhost:5173"
    echo "  📱 手機版: http://localhost:5173/m/"
else
    echo "  ❌ 未運行"
fi

echo ""

# 檢查端口佔用
echo "端口佔用情況:"
echo "  端口 8000: $(lsof -ti:8000 2>/dev/null | wc -l | xargs) 個進程"
echo "  端口 5173: $(lsof -ti:5173 2>/dev/null | wc -l | xargs) 個進程"

echo ""

# 檢查環境
echo "環境配置:"
if [ -f "$ROOT/frontend/.env" ]; then
    echo "  ✅ 前端 .env 文件存在"
    if grep -q "ALLOW_MANUAL_SYNC=false" "$ROOT/frontend/.env"; then
        echo "  🔒 同步按鈕: 隱藏 (生產環境)"
    else
        echo "  🔓 同步按鈕: 顯示 (開發環境)"
    fi
    APP_ENV=$(grep "APP_ENV=" "$ROOT/frontend/.env" | cut -d= -f2 || echo "development")
    echo "  🏷️  當前環境: $APP_ENV"
else
    echo "  ⚠️  前端 .env 文件不存在"
fi

echo ""

# 檢查數據庫
echo "數據庫:"
if [ -f "$ROOT/backend/data/goros.db" ]; then
    DB_SIZE=$(du -h "$ROOT/backend/data/goros.db" | cut -f1)
    echo "  ✅ 數據庫文件存在 ($DB_SIZE)"
    # 嘗試獲取商品數量
    if command -v sqlite3 &> /dev/null; then
        COUNT=$(sqlite3 "$ROOT/backend/data/goros.db" "SELECT COUNT(*) FROM products;" 2>/dev/null || echo "未知")
        echo "  📊 商品記錄數: $COUNT"
    fi
else
    echo "  ⚠️  數據庫文件不存在"
fi

echo ""
echo "🎯 快速指令:"
echo "  啟動服務: bash start.sh"
echo "  停止服務: 按 Ctrl+C"
echo "  生產模式: APP_ENV=production bash start.sh"
echo "  查看日誌: tail -f 終端輸出"