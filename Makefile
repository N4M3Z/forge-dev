# forge-dev Makefile

SKILL_SRC = skills
LIB_DIR  = $(or $(FORGE_LIB),lib)

# Fallbacks when common.mk is not yet available (uninitialized submodule)
INSTALL_SKILLS  ?= $(LIB_DIR)/bin/install-skills
VALIDATE_MODULE ?= $(LIB_DIR)/bin/validate-module

.PHONY: help install clean verify test lint check init

help:
	@echo "forge-dev management commands:"
	@echo "  make install         Install skills for all providers (SCOPE=workspace|user|all, default: workspace)"
	@echo "  make install-skills  Install skills for Claude, Gemini, Codex, and OpenCode"
	@echo "  make verify          Verify the full installation"
	@echo "  make clean           Remove previously installed skills"
	@echo "  make test            Run module validation"
	@echo "  make lint            Shellcheck all scripts + mdschema checks"
	@echo "  make check           Verify module structure"

init:
	@if [ ! -f $(LIB_DIR)/Cargo.toml ]; then \
	  echo "Initializing forge-lib submodule..."; \
	  git submodule update --init $(LIB_DIR); \
	fi

ifneq ($(wildcard $(LIB_DIR)/mk/common.mk),)
  include $(LIB_DIR)/mk/common.mk
  include $(LIB_DIR)/mk/skills/install.mk
  include $(LIB_DIR)/mk/skills/verify.mk
  include $(LIB_DIR)/mk/lint.mk
endif

install: install-skills
	@echo "Installation complete. Restart your session or reload skills."

clean: clean-skills

verify: verify-skills

test: $(VALIDATE_MODULE)
	@$(VALIDATE_MODULE) $(CURDIR)

lint: lint-schema lint-shell

check:
	@test -f module.yaml && echo "  ok module.yaml" || echo "  MISSING module.yaml"
	@test -f defaults.yaml && echo "  ok defaults.yaml" || echo "  MISSING defaults.yaml"
	@test -d skills && echo "  ok skills/" || echo "  MISSING skills/"
	@test -x "$(INSTALL_SKILLS)" && echo "  ok install-skills" || echo "  MISSING install-skills (run: make -C $(LIB_DIR) build)"
	@test -x "$(VALIDATE_MODULE)" && echo "  ok validate-module" || echo "  MISSING validate-module (run: make -C $(LIB_DIR) build)"
