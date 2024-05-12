# Continuous Integration:
# =======================
#
# Adapted from - https://github.com/jacebrowning/template-python
# Thanks @jacebrowning!
#
# ToDO:
# - sphinx   : Documentation generation.
# - napoleon : API documentation generation.

# Project settings
PROJECT := Hoyt.IO
PACKAGE := flask-server/hoyt
REPOSITORY := hoytnix/hoyt.io
PACKAGES := $(PACKAGE) flask-server/tests
CONFIG := $(shell ls flask-server/*.py)
MODULES := $(shell find $(PACKAGES) -name '*.py') $(CONFIG)

# Python settings
ifndef TRAVIS
	PYTHON_MAJOR ?= 3
	PYTHON_MINOR ?= 5
endif

# System paths
PLATFORM := $(shell python -c 'import sys; print(sys.platform)')
ifneq ($(findstring win32, $(PLATFORM)), )
	WINDOWS := true
	SYS_PYTHON_DIR := C:\\Python$(PYTHON_MAJOR)$(PYTHON_MINOR)
	SYS_PYTHON := $(SYS_PYTHON_DIR)\\python.exe
	# https://bugs.launchpad.net/virtualenv/+bug/449537
	export TCL_LIBRARY=$(SYS_PYTHON_DIR)\\tcl\\tcl8.5
else
	ifneq ($(findstring darwin, $(PLATFORM)), )
		MAC := true
	else
		LINUX := true
	endif
	SYS_PYTHON := python$(PYTHON_MAJOR)
	ifdef PYTHON_MINOR
		SYS_PYTHON := $(SYS_PYTHON).$(PYTHON_MINOR)
	endif
endif

# Virtual environment paths
REALPATH := $(shell python -c "import os; print(os.getcwd())")
ENV := $(REALPATH)/env
PYTHONPATH := $(ENV)/lib/python3.5
ifneq ($(findstring win32, $(PLATFORM)), )
	BIN := $(ENV)/Scripts
	ACTIVATE := $(BIN)/activate.bat
	OPEN := cmd /c start
else
	BIN := $(ENV)/bin
	ACTIVATE := . $(BIN)/activate
	ifneq ($(findstring cygwin, $(PLATFORM)), )
		OPEN := cygstart
	else
		OPEN := open
	endif
endif

# Virtual environment executables
ifndef TRAVIS
	BIN_ := $(BIN)/
endif
PYTHON := $(BIN_)python
PIP := $(BIN_)pip
EASY_INSTALL := $(BIN_)easy_install
HOYT := $(BIN_)hoyt

SNIFFER := $(BIN_)sniffer
HONCHO := $(ACTIVATE) && $(BIN_)honcho
YAPF := $(BIN_)yapf

# MAIN TASKS ###################################################################

.PHONY: all
all: doc

.PHONY: ci
ci: check test ## Run all tasks that determine CI status

.PHONY: watch
watch: install .clean-test ## Continuously run all CI tasks when files chanage
	$(SNIFFER)

.PHONY: run ## Start the program
run: install
	cd flask-server && $(HOYT) run

.PHONY: run_db ## Start the database
run_db:
	nohup $(PYTHON) database/monitor.py &
	cd database && docker-compose up --build

.PHONY: backup_db
backup_db:
	pg_dump -h localhost -p 5432 -U postgres -d hoyt -w --data-only --inserts -f database/backup.sql

.PHONY: compile
compile:
	@ echo "Nothing will happen if localhost:5000 isn't available."
	@ grep -q '200 OK' <<< $$(curl -Is http://localhost:5000 | head -1)
	cd flask-server && $(HOYT) freeze -e publish
	cd static-server && grunt

.PHONY: serve
serve: compile
	eval "sleep 3; xdg-open http://localhost:5001" &
	cd static-server && firebase serve

.PHONY: deploy
deploy: compile
	cd static-server && firebase deploy

# SYSTEM DEPENDENCIES ##########################################################

.PHONY: doctor
doctor:  ## Confirm system dependencies are available
	bin/verchew

# PROJECT DEPENDENCIES #########################################################

DEPS_CI := $(ENV)/.install-ci
DEPS_DEV := $(ENV)/.install-dev
DEPS_BASE := $(ENV)/.install-base

.PHONY: install
install: $(DEPS_CI) $(DEPS_DEV) $(DEPS_BASE) ## Install all project dependencies

$(DEPS_CI): flask-server/requirements-ci.txt $(PIP)
	$(PIP) install --upgrade -r $<
	@ touch $@  # flag to indicate dependencies are installed

$(DEPS_DEV): flask-server/requirements-dev.txt $(PIP)
	$(PIP) install --upgrade -r $<
ifdef WINDOWS
	@ echo "Manually install pywin32: https://sourceforge.net/projects/pywin32/files/pywin32"
else ifdef MAC
	$(PIP) install --upgrade pync MacFSEvents
else ifdef LINUX
	$(PIP) install --upgrade pyinotify
endif
	@ touch $@  # flag to indicate dependencies are installed

$(DEPS_BASE): flask-server/setup.py flask-server/requirements.txt $(PYTHON)
	$(PIP) install -e flask-server/
	@ touch $@  # flag to indicate dependencies are installed

$(PIP): $(PYTHON)
	$(PYTHON) -m pip install --upgrade pip setuptools
	@ touch $@

$(PYTHON):
	$(SYS_PYTHON) -m venv --clear $(ENV)

# CHECKS #######################################################################

PEP257 := $(BIN_)pep257
PYLINT := $(BIN_)pylint

.PHONY: check
check: pep257 pylint ## Run linters and static analysis

.PHONY: pep257
pep257: install ## Check for docstring issues
	$(PEP257) $(PACKAGES) $(CONFIG)

.PHONY: pylint
pylint: install ## Check for code issues
	$(PYLINT) $(PACKAGES) $(CONFIG) --rcfile=flask-server/.pylintrc

.PHONY: format
format: install ## Autoformat code
	cd flask-server && $(YAPF) -ri .

# TESTS ########################################################################

PYTEST := export PYTHONPATH=$(PYTHONPATH); $(BIN_)py.test
COVERAGE := $(BIN_)coverage
COVERAGE_SPACE := $(BIN_)coverage.space

RANDOM_SEED ?= $(shell date +%s)

PYTEST_CORE_OPTS := --doctest-modules -r xXw -vv
PYTEST_COV_OPTS := --cov=$(PACKAGE) --no-cov-on-fail --cov-report=term-missing --cov-report=html
PYTEST_RANDOM_OPTS := --random --random-seed=$(RANDOM_SEED)

PYTEST_OPTS := $(PYTEST_CORE_OPTS) $(PYTEST_COV_OPTS) $(PYTEST_RANDOM_OPTS)
PYTEST_OPTS_FAILFAST := $(PYTEST_OPTS) --last-failed --exitfirst

FAILURES := .cache/v/cache/lastfailed
REPORTS ?= xmlreport

.PHONY: test
test: test-all

.PHONY: test-unit
test-unit: install ## Run the unit tests
	@- mv $(FAILURES) $(FAILURES).bak
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGE) --junitxml=$(REPORTS)/unit.xml
	@- mv $(FAILURES).bak $(FAILURES)
	$(COVERAGE_SPACE) $(REPOSITORY) unit

.PHONY: test-int
test-int: install ## Run the integration tests
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_OPTS_FAILFAST) tests; fi
	$(PYTEST) $(PYTEST_OPTS) tests --junitxml=$(REPORTS)/integration.xml
	$(COVERAGE_SPACE) $(REPOSITORY) integration

.PHONY: test-all
test-all: install ## Run all the tests
	@ echo "Nothing will happen if the database isn't running."
	@ timeout 1 bash -c 'cat < /dev/null > /dev/tcp/localhost/5432'
	@ if test -e $(FAILURES); then $(PYTEST) $(PYTEST_OPTS_FAILFAST) $(PACKAGES); fi
	$(PYTEST) $(PYTEST_OPTS) $(PACKAGES) --junitxml=$(REPORTS)/overall.xml
	$(COVERAGE_SPACE) $(REPOSITORY) overall

.PHONY: read-coverage
read-coverage:
	$(OPEN) htmlcov/index.html

# DOCUMENTATION ################################################################

PYREVERSE := $(BIN_)pyreverse
PDOC := $(PYTHON) $(BIN_)pdoc
MKDOCS := $(BIN_)mkdocs

PDOC_INDEX := docs/apidocs/$(PACKAGE)/index.html
MKDOCS_INDEX := site/index.html

.PHONY: doc
doc: uml pdoc mkdocs ## Run documentation generators

.PHONY: uml
uml: install docs/*.png ## Generate UML diagrams for classes and packages
docs/*.png: $(MODULES)
	$(PYREVERSE) $(PACKAGE) -p $(PACKAGE) -a 1 -f ALL -o png --ignore tests
	- mv -f classes_$(PACKAGE).png docs/classes.png
	- mv -f packages_$(PACKAGE).png docs/packages.png

.PHONY: pdoc
pdoc: install $(PDOC_INDEX)  ## Generate API documentaiton with pdoc
$(PDOC_INDEX): $(MODULES)
	$(PDOC) --html --overwrite $(PACKAGE) --html-dir docs/apidocs
	@ touch $@

.PHONY: mkdocs
mkdocs: install $(MKDOCS_INDEX) ## Build the documentation site with mkdocs
$(MKDOCS_INDEX): mkdocs.yml docs/*.md
	ln -sf `realpath README.md --relative-to=docs` docs/index.md
	ln -sf `realpath CHANGELOG.md --relative-to=docs/about` docs/about/changelog.md
	ln -sf `realpath CONTRIBUTING.md --relative-to=docs/about` docs/about/contributing.md
	ln -sf `realpath LICENSE.md --relative-to=docs/about` docs/about/license.md
	$(MKDOCS) build --clean --strict

.PHONY: mkdocs-live
mkdocs-live: mkdocs ## Launch and continuously rebuild the mkdocs site
	eval "sleep 3; open http://127.0.0.1:8000" &
	$(MKDOCS) serve

# CLEANUP ######################################################################

.PHONY: clean
clean: .clean-dist .clean-test .clean-doc .clean-build ## Delete all generated and temporary files

.PHONY: clean-all
clean-all: clean .clean-env .clean-workspace

.PHONY: .clean-build
.clean-build:
	find $(PACKAGES) -name '*.pyc' -delete
	find $(PACKAGES) -name '__pycache__' -delete
	rm -rf *.egg-info

.PHONY: .clean-doc
.clean-doc:
	rm -rf README.rst docs/apidocs *.html docs/*.png site

.PHONY: .clean-test
.clean-test:
	rm -rf .cache .pytest .coverage htmlcov xmlreport

.PHONY: .clean-dist
.clean-dist:
	rm -rf *.spec dist build

.PHONY: .clean-env
.clean-env: clean
	rm -rf $(ENV)

.PHONY: .clean-workspace
.clean-workspace:
	rm -rf *.sublime-workspace

# HELP #########################################################################

.PHONY: help
help: all
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
