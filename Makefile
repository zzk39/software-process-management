.PHONY: help install backend admin student test lint build clean seed run-backend run-admin run-student all

help:
	@echo "常用命令："
	@echo "  make install        安装所有依赖（后端 + 两端前端）"
	@echo "  make seed           初始化数据库 + demo 数据"
	@echo "  make test           运行后端 pytest"
	@echo "  make build          构建两个前端 dist"
	@echo "  make run-backend    启动后端 8000"
	@echo "  make run-admin      启动管理端 5173"
	@echo "  make run-student    启动学生端 5174"
	@echo "  make all            一键冒烟：seed + test + build"
	@echo "  make clean          清理产物"

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd admin-web && npm install
	cd student-web && npm install

seed:
	cd backend && . .venv/bin/activate && rm -f study_seat.db && python -m app.seed

test:
	cd backend && . .venv/bin/activate && python -m pytest -q

build:
	cd admin-web && npm run build
	cd student-web && npm run build

run-backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

run-admin:
	cd admin-web && npm run dev

run-student:
	cd student-web && npm run dev

all: seed test build

clean:
	rm -rf backend/.venv backend/*.db backend/report.xml
	rm -rf admin-web/node_modules admin-web/dist
	rm -rf student-web/node_modules student-web/dist
