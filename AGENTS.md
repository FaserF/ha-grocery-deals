# AI Agent Reference for ha-grocery-deals

---

## Token Efficiency Rules (CRITICAL — Read First)

1. Output minimal prose. Bullet points only.
2. Short change summaries only (<=5 bullet points).
3. No repeating file content.
4. Targeted file reads only.
5. Suppress test output noise.

---

## Codebase Architecture

| Area | Path |
|---|---|
| Integration Entry | `custom_components/grocery_deals/__init__.py` |
| Coordinator | `custom_components/grocery_deals/coordinator.py` |
| Config & Options Flow | `custom_components/grocery_deals/config_flow.py` |
| Constants | `custom_components/grocery_deals/const.py` |
| Sensor Platform | `custom_components/grocery_deals/sensor.py` |
| Tests | `tests/` |

---

## CLI Commands

| Task | Command | Dir |
|---|---|---|
| Run tests | `pytest` | Root |
| Ruff linter | `ruff check . --fix` | Root |
| Ruff formatter | `ruff format .` | Root |
| mypy linter | `mypy .` | Root |
