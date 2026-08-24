#!/usr/bin/env bash
# Assemble the GitHub Pages site tree from downloaded component artifacts.
# Usage: assemble-pages-site.sh COMPONENTS_DIR OUT_DIR
#
# Contract with the deploy-pages reusable workflow: its `components` input
# selects which artifacts are fetched into COMPONENTS_DIR, but the component
# names and their internal layout are fixed here. The known components are:
#
#   site-blueprint/  homepage/ (Jekyll-built site root), blueprint/ (web
#                    blueprint), blueprint.pdf, and optional blueprint-*.pdf
#                    excerpt volumes                                (required)
#   site-docs/       docs/ (doc-gen4 API docs) and paper-gaps/ PDFs (optional)
#   site-badges/     badge endpoint *.json                          (optional)
#
# Directories with other names are ignored. A repo that produces a new
# component must teach this script about it.
set -euo pipefail

COMPONENTS="$1"
OUT="$2"

if [ ! -d "$COMPONENTS/site-blueprint" ]; then
  echo "::error::site-blueprint component missing — cannot assemble site"
  exit 1
fi

mkdir -p "$OUT"

echo "==> Homepage..."
cp -r "$COMPONENTS/site-blueprint/homepage/." "$OUT/"
# Any badge JSON shipped inside the homepage is stale; live values come from
# the site-badges component below.
rm -rf "$OUT/badges"

echo "==> Blueprint..."
mkdir -p "$OUT/blueprint"
cp -r "$COMPONENTS/site-blueprint/blueprint/." "$OUT/blueprint/"
cp "$COMPONENTS/site-blueprint/blueprint.pdf" "$OUT/blueprint.pdf"
# Optional excerpt volumes (e.g. blueprint-ch01-12.pdf) ride along by name.
for pdf in "$COMPONENTS/site-blueprint"/blueprint-*.pdf; do
  if [ -f "$pdf" ]; then
    cp "$pdf" "$OUT/$(basename "$pdf")"
  fi
done

if [ -d "$COMPONENTS/site-docs/docs" ]; then
  echo "==> API docs..."
  cp -r "$COMPONENTS/site-docs/docs" "$OUT/docs"
else
  echo "::warning::site-docs component missing — deploying without API docs (the next docgen run restores them)"
fi
if [ -d "$COMPONENTS/site-docs/paper-gaps" ]; then
  echo "==> Paper-gap PDFs..."
  cp -r "$COMPONENTS/site-docs/paper-gaps" "$OUT/paper-gaps"
fi

if [ -d "$COMPONENTS/site-badges" ]; then
  echo "==> Badges..."
  mkdir -p "$OUT/badges"
  cp "$COMPONENTS/site-badges"/*.json "$OUT/badges/"
else
  echo "::warning::site-badges component missing — deploying without badge endpoints"
fi

echo "==> Site assembled at $OUT"
du -sh "$OUT"
