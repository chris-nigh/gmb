# Claude-Specific Hooks for GMB

This file configures hooks that run when **Claude Code** performs git operations.

**Note:** For standard git pre-commit hooks that apply to all developers, see `.pre-commit-config.yaml` and install with `pre-commit install`.

## Configuration

```yaml
hooks:
  user-prompt-submit:
    # Clean up temporary files before Claude commits
    - event: before
      command: git commit
      bash: |
        set -e
        echo "🧹 Cleaning up temporary files..."

        # Remove CSV files from standalone runs (not in data/ directory)
        find . -maxdepth 1 -name "*.csv" -type f -delete 2>/dev/null || true

        # Remove other temporary files
        find . -maxdepth 1 -name "*.tmp" -type f -delete 2>/dev/null || true
        find . -maxdepth 1 -name "*.log" -type f -delete 2>/dev/null || true

        # Check if any files were in staging that got deleted
        git add -u

        echo "✅ Cleanup complete"
```

## What This Hook Does

This Claude-specific hook runs automatically before Claude makes a commit and:

1. **Removes temporary CSV files** generated from standalone script runs (in project root only, preserves data/ directory)
2. **Removes .tmp and .log files** from the project root
3. **Updates staging** to reflect any deleted files

## Why Claude-Specific?

This hook handles cleanup tasks that are specific to Claude's workflow:
- Claude might generate CSV files during testing/analysis
- Ensures clean commits without manual intervention
- Doesn't interfere with your manual workflow

## Standard Pre-commit Hooks

For the full CI checks (tests, linting, formatting, type checking), the project uses the standard `pre-commit` framework configured in `.pre-commit-config.yaml`.

To install those hooks:
```bash
uv pip install pre-commit
pre-commit install
```
