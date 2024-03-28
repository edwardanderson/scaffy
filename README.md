# Scaffy

Scaffy is a static site knowledge base generator for [Articular](https://github.com/edwardanderson/articular).

## Install

> [!WARNING]
> Scaffy is an on-going research project and is not yet ready for use in production.

```bash
git clone https://github.com/edwardanderson/scaffy.git
cd scaffy/
python3.10 -m venv .venv
source .venv/bin/activate
pip install --editable .
```

## Quickstart

Build the example dataset as a knowledge base.

```bash
cd scaffy/examples/kings_and_queens/
scaffy build
```

Explore `site/`.
