#!/usr/bin/env bash
# 本地冒烟脚本：seed + 启动后端 + 用 curl 走一遍主链路
# 用法：./scripts/smoke.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

# 激活虚拟环境
if [ ! -d .venv ]; then
    echo "→ 创建 venv"
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -q -r requirements.txt
else
    . .venv/bin/activate
fi

echo "→ 重置并 seed"
rm -f study_seat.db
python -m app.seed

if lsof -i :8000 >/dev/null 2>&1; then
    echo "❌ 端口 8000 被占用，请先释放" >&2
    exit 1
fi

echo "→ 启动后端（后台）"
uvicorn app.main:app --port 8000 >/tmp/sr_backend.log 2>&1 &
PID=$!
trap "kill $PID 2>/dev/null || true" EXIT

# 等待就绪
for i in {1..30}; do
    if curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then break; fi
    sleep 0.5
done
if ! curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then
    echo "❌ 后端启动失败，日志：" >&2
    cat /tmp/sr_backend.log >&2
    exit 1
fi

echo "→ 学生登录"
TOKEN=$(curl -sf -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"student_no":"20230001","password":"123456"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["access_token"])')
echo "  token: ${TOKEN:0:20}..."

echo "→ 浏览自习室"
curl -sf http://localhost:8000/api/rooms -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20

echo "→ 创建预约（明天 10:00, 2h, 座位 1）"
START=$(python3 -c "from datetime import datetime, timedelta, UTC; print((datetime.now(UTC)+timedelta(days=1)).replace(hour=10,minute=0,second=0,microsecond=0,tzinfo=None).isoformat())")
RESV_RES=$(curl -sf -X POST http://localhost:8000/api/reservations \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"seat_id\":1,\"start_at\":\"$START\",\"hours\":2}")
echo "  $RESV_RES"
RID=$(echo "$RESV_RES" | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["id"])')

echo "→ 我的预约"
curl -sf http://localhost:8000/api/reservations/me -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo "→ 取消预约 #$RID"
curl -sf -X POST "http://localhost:8000/api/reservations/$RID/cancel" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo
echo "✅ 冒烟通过"
