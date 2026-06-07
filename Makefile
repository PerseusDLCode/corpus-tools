# Makefile for Perseus corpus normalization and auditing
#
# Usage:
#   make audit FILES="path/to/*.xml"
#   make audit-refs FILES="path/to/*.xml" OUT=reports/
#   make normalize FILES="path/to/*.xml" GENRE=prose-historiography OUT=normalized/
#   make validate FILES="path/to/*.xml"
#   make pipeline FILES="path/to/*.xml" GENRE=verse-epic OUT=normalized/

CT        := .venv/bin/corpus-tools
AUDIT_REF := .venv/bin/audit-refs
AUDIT_STR := .venv/bin/audit-structure
AUDIT_SCH := .venv/bin/audit-schema
SCH          := schematron/perseus_normalized.sch
ENCODING_SCH := schematron/perseus_encoding.sch

FILES ?= $(error FILES is required: make <target> FILES="path/to/*.xml")
GENRE ?= $(error GENRE is required for set-genre: make set-genre FILES=... GENRE=prose-historiography)
OUT   ?=

# --- pipeline ----------------------------------------------------------------

.PHONY: set-genre
set-genre:  ## Annotate files with Perseus genre: FILES="..." GENRE=prose-historiography [OUT=dir/]
	$(CT) set-genre $(FILES) --genre $(GENRE) $(if $(OUT),-o $(OUT))

.PHONY: normalize
normalize:  ## Run normalization pipeline: FILES="..." [OUT=dir/]
	$(CT) normalize $(FILES) $(if $(OUT),-o $(OUT))

.PHONY: validate
validate:  ## Validate normalized files against pipeline schema: FILES="..."
	$(CT) validate $(FILES) --schema $(SCH)

.PHONY: pipeline
pipeline: set-genre normalize  ## set-genre then normalize: FILES="..." GENRE=... [OUT=dir/]

# --- audit -------------------------------------------------------------------

.PHONY: audit-refs
audit-refs:  ## Audit CTS citation references: FILES="..." [OUT=dir/]
	$(AUDIT_REF) $(FILES) $(if $(OUT),-o $(OUT))

.PHONY: audit-structure
audit-structure:  ## Audit div/milestone structure: FILES="..." [OUT=dir/]
	$(AUDIT_STR) $(FILES) $(if $(OUT),-o $(OUT))

.PHONY: audit-schema
audit-schema:  ## Audit encoding anomalies (Schematron): FILES="..." [OUT=dir/]
	$(AUDIT_SCH) $(FILES) --schema $(ENCODING_SCH) $(if $(OUT),-o $(OUT))

.PHONY: audit
audit: audit-refs audit-structure audit-schema  ## Run all auditors: FILES="..." [OUT=dir/]

# --- dev ---------------------------------------------------------------------

.PHONY: install
install:  ## Install dependencies into .venv
	pdm install

.PHONY: test
test:  ## Run test suite
	.venv/bin/pytest

.PHONY: lint
lint:  ## Lint source
	.venv/bin/ruff check src tests

.PHONY: typecheck
typecheck:  ## Run mypy
	.venv/bin/mypy src

.PHONY: help
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
