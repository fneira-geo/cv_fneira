.PHONY: all full exec ats simple

all: full exec ats

full:
	uv run python build.py --full

exec:
	uv run python build.py --exec

ats:
	uv run python build.py --ats

## Build all templates with sans-serif style variant
simple:
	uv run python build.py --style simple
