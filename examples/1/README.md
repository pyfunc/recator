# Recator Examples - 1

A minimal TypeScript example with intentionally duplicated blocks to demonstrate Recator’s detection and reporting capabilities.

## Files

- `alpha.ts`
- `beta.ts`
- `gamma.ts`

Each file contains a 7-line HTML escaping block duplicated across files.

## Run

From repository root:

```bash
# Show duplicates with snippet and all occurrences
recator examples/1 --analyze --languages javascript \
  --min-lines 7 --min-tokens 15 \
  --show-snippets --max-show 0 --max-blocks 0 -v

# Suppress redundant groups (default) vs show all groups
recator examples/1 --analyze --languages javascript --min-lines 7 -v
recator examples/1 --analyze --languages javascript --min-lines 7 -v --no-suppress-duplicates

# Interactive refactor preview for selected duplicates
recator examples/1 --refactor --interactive --dry-run --show-snippets
```
