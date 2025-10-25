#!/usr/bin/env bash
# Generate TypeScript types and stage them for commit

set -e

# Generate types
python scripts/generate_types.py

# Stage the generated file
git add frontend/src/types/generated.ts
