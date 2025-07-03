# Makefile for 16-pixels project (Docker-only)

# Variables
DOCKER_IMAGE := 16-pixels
DOCKER_TEST_IMAGE := 16-pixels-test
DOCKER_UI_IMAGE := 16-pixels-ui
DOCKER_RUN := docker run --rm -v $$(pwd)/output:/app/output --env-file .env
UI_PORT ?= 8080

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "16-Pixels Project Makefile (Docker)"
	@echo "=================================="
	@echo "Available targets:"
	@echo "  make build        - Build Docker images"
	@echo "  make run          - Run the application (requires QUERY parameter)"
	@echo "  make test         - Run integration tests"
	@echo "  make clean        - Remove Docker images"
	@echo ""
	@echo "UI targets:"
	@echo "  make build-ui     - Build UI Docker image"
	@echo "  make start-ui     - Start UI server (default port: 8080)"
	@echo "  make stop-ui      - Stop UI server"
	@echo "  make restart-ui   - Restart UI server"
	@echo ""
	@echo "Examples:"
	@echo "  make run QUERY='a cute pixel art cat'"
	@echo "  make run QUERY='retro game warrior' VARIATIONS=4"
	@echo "  make run QUERY='pixel art mushroom' DEBUG=1"
	@echo "  make start-ui UI_PORT=8090  # Start UI on custom port"

# Build Docker images
.PHONY: build
build:
	@echo "Building Docker images..."
	@docker build -t $(DOCKER_IMAGE) -f Dockerfile .
	@docker build -t $(DOCKER_TEST_IMAGE) -f Dockerfile.test .
	@echo "✓ Docker images built"

# Run the application
.PHONY: run
run:
ifndef QUERY
	@echo "Error: QUERY parameter is required"
	@echo "Usage: make run QUERY='your image query'"
	@exit 1
endif
	@echo "Running 16-pixels with query: $(QUERY)"
	@$(DOCKER_RUN) $(DOCKER_IMAGE) \
		--query "$(QUERY)" \
		$(if $(VARIATIONS),--variations $(VARIATIONS)) \
		$(if $(OUTPUT_DIR),--output-dir $(OUTPUT_DIR)) \
		$(if $(NO_PIXEL_ART),--no-pixel-art) \
		$(if $(DEBUG),--debug)

# Run tests
.PHONY: test
test:
	@echo "Running integration tests..."
	@docker run --rm \
		--env-file .env \
		-v $$(pwd)/test-output:/app/test-output \
		$(DOCKER_TEST_IMAGE)

# Run with docker-compose
.PHONY: compose-run
compose-run:
ifndef QUERY
	@echo "Error: QUERY parameter is required"
	@echo "Usage: make compose-run QUERY='your image query'"
	@exit 1
endif
	@docker-compose run --rm app \
		--query "$(QUERY)" \
		$(if $(VARIATIONS),--variations $(VARIATIONS)) \
		$(if $(NO_PIXEL_ART),--no-pixel-art) \
		$(if $(DEBUG),--debug)

# Run tests with docker-compose
.PHONY: compose-test
compose-test:
	@docker-compose run --rm test

# Build with docker-compose
.PHONY: compose-build
compose-build:
	@docker-compose build

# View latest output
.PHONY: view-output
view-output:
	@if [ -d "output" ]; then \
		latest=$$(ls -t output | head -n1); \
		if [ -n "$$latest" ]; then \
			echo "Latest output: output/$$latest"; \
			ls -la output/$$latest/*/; \
		else \
			echo "No output found"; \
		fi \
	else \
		echo "Output directory does not exist"; \
	fi

# Shell into the container for debugging
.PHONY: shell
shell:
	@$(DOCKER_RUN) -it --entrypoint /bin/bash $(DOCKER_IMAGE)

# Run with example query
.PHONY: example
example:
	@$(MAKE) run QUERY="a cute pixel art cat"

# Build and run
.PHONY: build-run
build-run: build
	@$(MAKE) run QUERY="$(QUERY)"

# Clean Docker images
.PHONY: clean
clean:
	@echo "Removing Docker images..."
	@docker rmi $(DOCKER_IMAGE) 2>/dev/null || true
	@docker rmi $(DOCKER_TEST_IMAGE) 2>/dev/null || true
	@docker rmi $(DOCKER_UI_IMAGE) 2>/dev/null || true
	@echo "✓ Docker images removed"

# Show Docker images
.PHONY: images
images:
	@docker images | grep -E "$(DOCKER_IMAGE)|$(DOCKER_TEST_IMAGE)" || echo "No 16-pixels images found"

# Tail logs (when using docker-compose)
.PHONY: logs
logs:
	@docker-compose logs -f

# Check if .env file exists
.PHONY: check-env
check-env:
	@if [ ! -f ".env" ]; then \
		echo "Warning: .env file not found. Creating from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env and add your API keys"; \
		exit 1; \
	fi

# Run all: build and test
.PHONY: all
all: build test

# Quick test with all defaults
.PHONY: quick-test
quick-test: check-env build
	@$(MAKE) run QUERY="pixel art test image"

# UI targets
.PHONY: build-ui
build-ui:
	@echo "Building UI Docker image..."
	@docker build -t $(DOCKER_UI_IMAGE) -f Dockerfile.ui .
	@echo "✓ UI Docker image built"

.PHONY: start-ui
start-ui:
	@echo "Starting UI server on port $(UI_PORT)..."
	@docker run -d \
		--name 16-pixels-ui \
		-p $(UI_PORT):8080 \
		-v $$(pwd)/output:/app/output:ro \
		-e UI_PORT=8080 \
		$(DOCKER_UI_IMAGE)
	@echo "✓ UI server started at http://localhost:$(UI_PORT)"

.PHONY: stop-ui
stop-ui:
	@echo "Stopping UI server..."
	@docker stop 16-pixels-ui 2>/dev/null && docker rm 16-pixels-ui 2>/dev/null || true
	@echo "✓ UI server stopped"

.PHONY: restart-ui
restart-ui: stop-ui start-ui