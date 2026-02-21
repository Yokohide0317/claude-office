.PHONY: install install-all dev backend frontend simulate checkall lint fmt test typecheck \
	test-opencode-adapter \
	clean clean-db clean-all \
	dev-tmux dev-tmux-kill dev-tmux-backend dev-tmux-frontend \
	build-static \
	docker-build docker-up docker-down docker-logs docker-shell

# Detect package manager: prefer bun if available, otherwise use npm
PKG_MGR := $(shell command -v bun >/dev/null 2>&1 && echo "bun" || echo "npm")
PKG_INSTALL := $(shell command -v bun >/dev/null 2>&1 && echo "bun install" || echo "npm install")

install:
	cd backend && uv sync
	cd frontend && $(PKG_INSTALL)

install-all: install
	@echo "All components installed"

dev:
	@echo "Starting backend and frontend in parallel..."
	@make -j 2 backend frontend

backend:
	make -C backend dev

frontend:
	make -C frontend dev

# Build static frontend and copy to backend for serving
build-static:
	make -C frontend build-static
	@echo "Frontend built and copied to backend/static"
	@echo "Start backend with 'make backend' to serve at http://localhost:8000"

simulate:
	uv run python scripts/simulate_events.py

test-agent:
	uv run python scripts/test_single_agent.py

test-opencode-adapter:
	uv run python scripts/test_opencode_adapter.py

lint:
	make -C backend lint
	make -C frontend lint

fmt:
	make -C backend fmt
	make -C frontend fmt

test:
	make -C backend test
	make -C frontend test

typecheck:
	make -C backend typecheck
	make -C frontend typecheck

checkall:
	make -C backend checkall
	make -C frontend checkall

# tmux-based dev targets for better monitoring
TMUX_SESSION=opencode-office

dev-tmux:
	@if tmux has-session -t $(TMUX_SESSION) 2>/dev/null; then \
		echo "Session $(TMUX_SESSION) already exists. Use 'make dev-tmux-kill' first or attach with 'tmux attach -t $(TMUX_SESSION)'"; \
	else \
		tmux new-session -d -s $(TMUX_SESSION) -n backend; \
		tmux send-keys -t $(TMUX_SESSION):backend "cd $(CURDIR)/backend && make dev" Enter; \
		tmux new-window -t $(TMUX_SESSION) -n frontend; \
		tmux send-keys -t $(TMUX_SESSION):frontend "cd $(CURDIR)/frontend && make dev" Enter; \
		tmux select-window -t $(TMUX_SESSION):backend; \
		echo "Started tmux session '$(TMUX_SESSION)' with backend and frontend windows"; \
		echo "Attach with: tmux attach -t $(TMUX_SESSION)"; \
	fi

dev-tmux-kill:
	@tmux kill-session -t $(TMUX_SESSION) 2>/dev/null && echo "Killed tmux session $(TMUX_SESSION)" || echo "No session to kill"

dev-tmux-backend:
	@tmux send-keys -t $(TMUX_SESSION):backend C-c 2>/dev/null || true
	@sleep 1
	@tmux send-keys -t $(TMUX_SESSION):backend "make dev" Enter 2>/dev/null || echo "Session not found"

dev-tmux-frontend:
	@tmux send-keys -t $(TMUX_SESSION):frontend C-c 2>/dev/null || true
	@sleep 1
	@tmux send-keys -t $(TMUX_SESSION):frontend "make dev" Enter 2>/dev/null || echo "Session not found"

# Cleanup targets
clean-db:
	rm -f backend/visualizer.db
	@echo "Database removed"

clean:
	rm -rf frontend/.next

clean-all: clean clean-db
	@echo "All build artifacts and data cleaned"

# Docker targets
docker-build:
	docker compose build

docker-up:
	docker compose up -d
	@echo "OpenCode Office running at http://localhost:8000"

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-shell:
	docker compose exec claude-office /bin/bash
