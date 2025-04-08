# Color Milker Makefile
# Installs the application so it can be run as 'cmilker' from terminal

PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin
INSTALL_PATH = $(shell pwd)
VENV_PATH = $(INSTALL_PATH)/.venv

.PHONY: install uninstall clean deps

install: cmilker
	@echo "Installing cmilker to $(BINDIR)..."
	@mkdir -p $(BINDIR)
	@cp cmilker $(BINDIR)/cmilker
	@chmod +x $(BINDIR)/cmilker
	@sed -i '' "s|INSTALL_DIR_PLACEHOLDER|$(INSTALL_PATH)|g" $(BINDIR)/cmilker
	@sed -i '' "s|VENV_DIR_PLACEHOLDER|$(VENV_PATH)|g" $(BINDIR)/cmilker
	@echo "Installation complete. You can now run 'cmilker' from anywhere."

cmilker:
	@echo "#!/bin/bash" > cmilker
	@echo "# Color Milker terminal wrapper" >> cmilker
	@echo "INSTALL_DIR=INSTALL_DIR_PLACEHOLDER" >> cmilker
	@echo "VENV_DIR=VENV_DIR_PLACEHOLDER" >> cmilker
	@echo "" >> cmilker
	@echo "# Activate virtual environment if it exists" >> cmilker
	@echo "if [ -f \"\$$VENV_DIR/bin/activate\" ]; then" >> cmilker
	@echo "    source \"\$$VENV_DIR/bin/activate\"" >> cmilker
	@echo "fi" >> cmilker
	@echo "" >> cmilker
	@echo "# Run the application" >> cmilker
	@echo "python \"\$$INSTALL_DIR/src/main.py\" \"\$$@\"" >> cmilker
	@echo "" >> cmilker
	@chmod +x cmilker
	@echo "Created cmilker wrapper script"

deps:
	@echo "Installing dependencies..."
	@python -m venv .venv
	@.venv/bin/pip install PyQt6
	@echo "Dependencies installed"

uninstall:
	@echo "Uninstalling cmilker..."
	@rm -f $(BINDIR)/cmilker
	@echo "Uninstallation complete"

clean:
	@echo "Cleaning up..."
	@rm -f cmilker
	@echo "Cleanup complete" 