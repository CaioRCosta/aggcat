# aggcat
> A simple CLI to aggregate code analysis tools and metrics in one place.

[![CI](https://github.com/CaioRCosta/aggcat/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CaioRCosta/aggcat/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CaioRCosta/aggcat/branch/main/graph/badge.svg)](https://codecov.io/gh/CaioRCosta/aggcat)
[![Commits](https://img.shields.io/github/commit-activity/t/CaioRCosta/aggcat?label=commits&style=flat)](https://github.com/CaioRCosta/aggcat/commits/main)
[![Contributors](https://img.shields.io/github/contributors/CaioRCosta/aggcat?style=flat)](https://github.com/CaioRCosta/aggcat/graphs/contributors)
[![Pull Requests](https://img.shields.io/github/issues-pr/CaioRCosta/aggcat?label=pull%20requests&style=flat)](https://github.com/CaioRCosta/aggcat/pulls)
[![License](https://img.shields.io/github/license/CaioRCosta/aggcat?style=flat)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/CaioRCosta/aggcat?style=flat)](https://github.com/CaioRCosta/aggcat/commits/main)

---

## Group Members

- Ari Gonçalves da Silva Filho
- Caio Rodrigues Costa
- Túlio Henrique Rodrigues Costa

---

## What is it?

**aggcat** is a lightweight command-line tool that helps you run multiple code analysis tools together and consolidates their results into a single, actionable report.

It targets **software maintenance and evolution** problems by mining repository history and static code metrics — making it easier to spot code smells, track quality trends, identify risky hotspots, and keep your codebase clean.

---

## Why use it?

- 🔍 **Detect issues faster** — run 10+ tools with a single command
- 📊 **Centralize metrics** — one report instead of ten scattered outputs
- 🧩 **Avoid tool fragmentation** — no more switching between Lizard, Radon, Bandit, etc.
- 🚀 **Improve code quality with less effort** — prioritize what actually matters

---

## Technologies

| Layer | Technology | Purpose |
|:---|:---|:---|
| **CLI** | [Typer](https://typer.tiangolo.com/) | Command-line interface and argument parsing |
| **Git mining** | [PyDriller](https://pydriller.readthedocs.io/) | Commit history, code churn, file evolution |
| **Git metadata** | [GitPython](https://gitpython.readthedocs.io/) | Branch analysis, author mapping, truck factor |
| **GitHub API** | [PyGithub](https://pygithub.readthedocs.io/) | Issues, pull requests, process metrics |
| **Complexity** | [Lizard](https://github.com/terryyin/lizard) | Cyclomatic complexity per function/file |
| **Maintainability** | [Radon](https://radon.readthedocs.io/) | Maintainability Index and Halstead metrics |
| **Line counts** | [Cloc](https://github.com/AlDanial/cloc) | Code vs. comment volume |
| **Style** | [Flake8](https://flake8.pycqa.org/) | PEP 8 violations and stylistic debt |
| **Security** | [Bandit](https://bandit.readthedocs.io/) | Known security flaws in Python code |
| **AST (Python)** | [Python AST](https://docs.python.org/3/library/ast.html) | Nesting depth, structural complexity |
| **AST (multi-lang)** | [Tree-sitter](https://tree-sitter.github.io/) | Anti-pattern detection across languages |
| **Dead code** | [Vulture](https://github.com/jendrikseipp/vulture) | Unused functions, variables and imports |
| **Dependencies** | [pip-audit](https://github.com/pypa/pip-audit) | Known CVEs in project dependencies |
| **Coupling** | [importlib](https://docs.python.org/3/library/importlib.html) | Module dependency graph (fan-in/fan-out) |
| **Test coverage** | [coverage.py](https://coverage.readthedocs.io/) | Line coverage crossed with complexity |
| **Testing** | [pytest](https://pytest.org/) | Unit test framework |
| **CI** | [GitHub Actions](https://github.com/features/actions) | Automated test execution on every push |

---

## Installation

### Requirements

- Python 3.11+
- `cloc` installed on your system ([install guide](https://github.com/AlDanial/cloc#install-via-package-manager))

### From source

```bash
# Clone the repository
git clone https://github.com/CaioRCosta/aggcat.git
cd aggcat

# Install in editable mode with all dependencies
pip install -e ".[dev]"
```

### Verify installation

```bash
aggcat --help
```

---

## Usage

### Commands

| Command | Description |
|:---|:---|
| `aggcat analyze <repo>` | Analyze a local Git repository |
| `aggcat config show` | Show current configuration for all tools and composites |
| `aggcat config set <name> <key> <value>` | Override a configuration constant |
| `aggcat config reset` | Reset all configuration to defaults |
| `aggcat version` | Print the installed version |

---

### `aggcat analyze`

```
aggcat analyze [OPTIONS] REPO
```

| Option | Short | Default | Description |
|:---|:---|:---|:---|
| `--output` | `-o` | `terminal` | Output format: `terminal` \| `json` \| `html` |
| `--top-n` | `-n` | all | Limit results to top N items per section |
| `--all` | `-a` | `false` | Run all tools, skipping the interactive selector |

By default, `aggcat analyze` opens an **interactive tool selector** where you can pick which tools and composite reports to run using arrow keys, Space to toggle, and Enter to confirm. Tools are grouped into two sections:

```
── Tools ──────────────────────────────────────
> [✔] radon           - Calculates the Maintainability Index...
  [✔] bandit          - Detects security vulnerabilities...
  ...
── Composite Reports ──────────────────────────
  [✔] hotspots        - Files with high churn AND high complexity... [uses: pydriller, lizard]
  [✔] truck_factor    - Files concentrated in few developers... [uses: gitpython]
  ...
```

A **progress bar** is shown during analysis, indicating the current tool being executed.

#### GitHub metrics

GitHub process metrics are fetched automatically when a `GITHUB_TOKEN` environment variable is set and the repository has a GitHub remote origin configured in `.git/config`. No flags needed — the slug is detected automatically.

```bash
export GITHUB_TOKEN=ghp_yourtoken
aggcat analyze /path/to/repo
```

If no token is provided, the GitHub tool is shown in the selector as unavailable (greyed out).

#### Examples

```bash
# Interactive selector, all results shown
aggcat analyze /path/to/repo

# Skip selector — run all tools at once
aggcat analyze /path/to/repo --all

# Output as HTML report
aggcat analyze /path/to/repo --output html

# Output as JSON
aggcat analyze /path/to/repo --output json

# Limit each section to top 10 results
aggcat analyze /path/to/repo --top-n 10

# Skip selector, limit to top 5, output HTML
aggcat analyze /path/to/repo --all --top-n 5 --output html
```

---

### `aggcat config`

Tools and composite reports expose configurable thresholds you can tune per-project.

```bash
# See all configurable values and their current/default state
aggcat config show

# Override a value (cast automatically to the correct type)
aggcat config set lizard cc_low 15
aggcat config set radon mi_grade_a 85.0
aggcat config set hotspots min_churn 3
aggcat config set truck_factor max_authors 3

# Reset everything back to defaults
aggcat config reset
```

#### Configurable constants

| Tool / Composite | Key | Default | Description |
|:---|:---|:---|:---|
| `radon` | `mi_grade_a` | `80.0` | MI score threshold for grade A |
| `radon` | `mi_grade_b` | `60.0` | MI score threshold for grade B |
| `radon` | `mi_grade_c` | `40.0` | MI score threshold for grade C |
| `lizard` | `cc_low` | `10` | Cyclomatic complexity warning threshold |
| `vulture` | `min_confidence` | `80` | Minimum confidence % for dead code findings |
| `ast_nesting` | `max_depth` | `3` | Maximum allowed control-flow nesting depth |
| `hotspots` | `min_churn` | `5` | Minimum commit churn to qualify as a hotspot |
| `hotspots` | `min_cc` | `10` | Minimum cyclomatic complexity for hotspot |
| `truck_factor` | `max_authors` | `2` | Maximum authors before a file is excluded from risk |
| `uncovered_complex` | `max_coverage` | `60.0` | Coverage % below which a file is considered under-tested |
| `uncovered_complex` | `min_cc` | `10` | Minimum CC to flag as uncovered-complex |
| `bandit_risk` | `min_cc` | `1` | Minimum CC for a security finding to appear in the report |

---

## Composite Reports

Composite reports combine the output of multiple base tools to surface cross-cutting insights that no single tool can provide alone.

| Report | Depends on | What it surfaces |
|:---|:---|:---|
| 🔴 **Hotspots** | PyDriller × Lizard | Files with high churn **and** high complexity — highest refactoring risk |
| 🟡 **Truck Factor** | GitPython | Files concentrated in ≤ N developers — bus factor risk |
| ⚠️ **Uncovered Complex** | coverage.py × Lizard | Complex files with low test coverage — highest risk to change |
| 🛡️ **Bandit Risk** | Bandit × Lizard | Security issues ranked by file complexity — harder-to-fix flaws first |

---

## Tools & Metrics

| # | Tool | Category | Metric | Contribution |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **PyDriller** | Evolution / Git | Modification frequency (*Code Churn*) per file | **Instability Factor:** Crossed with complexity to find the most critical *Hotspots* |
| **2** | **GitPython** | Evolution / Git | Active branches count and unique authors per file | **Bottleneck Factor (*Truck Factor*):** Identifies critical files concentrated in few developers |
| **3** | **PyGithub** | Evolution / GitHub | Average Issue open time and Pull Request metrics | **Process Factor:** Relates code complexity with delivery time and problem resolution |
| **4** | **Lizard** | Code Metrics | Cyclomatic Complexity (execution paths) | **Rigidity Factor:** Identifies code that is hard to test and change; base for the refactoring list |
| **5** | **Radon** | Code Metrics | Maintainability Index (0–100) and Halstead metrics | **Code Health:** Defines the base maintainability score for each Python file |
| **6** | **Cloc** | Code Metrics | Volume of pure code lines vs. comment lines | **Documentation Factor:** Penalizes large, dense files with no minimum documentation |
| **7** | **Flake8** | Code Quality | Style and formatting violations (PEP 8 standard) | **Stylistic Technical Debt:** Measures the level of carelessness or lack of standardization |
| **8** | **Bandit** | Code Quality | Known security flaws (e.g., exposed passwords, `eval`) | **Risk Factor:** Raises correction priority when the flaw is in a complex area (Lizard) |
| **9** | **Python AST** | Code Parsers | Native syntax tree (nested `if`/`for` block count) | **Structural Complexity:** Visually details why a file has high complexity (spaghetti code) |
| **10** | **Tree-sitter** | Code Parsers | Precise multi-language abstract syntax tree | **Anti-patterns:** Identifies serious architectural mistakes such as empty `except:` blocks |
| **11** | **Vulture** | Code Quality | Dead code — unused functions, variables and imports | **Entropy Factor:** Identifies accumulation of obsolete code that increases cognitive load without adding value |
| **12** | **pip-audit** | Security | Known vulnerabilities in dependencies (CVEs) | **External Risk Factor:** Complements Bandit (own code) with risks from the dependency chain |
| **13** | **importlib** | Structure | Internal module dependency graph (coupling) | **Coupling Factor:** Detects modules with high fan-in/fan-out, candidates for breakpoints in refactoring |
| **14** | **coverage.py** | Testing | Percentage of lines covered by automated tests | **Confidence Factor:** Crosses low coverage with high complexity (Lizard) to find critical unprotected zones |

---

## Running Tests Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run a specific test file
pytest tests/tools/test_bandit.py -v
```

Tests are also executed automatically on every push and pull request via GitHub Actions (see `.github/workflows/ci.yml`).

---
