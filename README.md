# aggcat
> A simple CLI to aggregate code analysis tools and metrics in one place.

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
git clone https://github.com/<your-org>/aggcat.git
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

### Analyze a local repository

```bash
aggcat analyze /path/to/your/repo
```

### Analyze with a specific output format

```bash
# Terminal output (default)
aggcat analyze /path/to/repo --output terminal

# JSON report
aggcat analyze /path/to/repo --output json

# HTML report
aggcat analyze /path/to/repo --output html
```

### Include GitHub metrics (requires a token)

```bash
export GITHUB_TOKEN=your_token_here
aggcat analyze /path/to/repo --github-repo owner/repo-name
```

### Example output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  aggcat report — my-project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔴 Hotspots (high churn + high complexity)
     src/core/parser.py   churn=42  CC=18
     src/api/handler.py   churn=31  CC=14

  🟡 Truck Factor Risk
     src/db/models.py     authors=1  commits=87

  🟢 Maintainability
     src/utils/helpers.py  MI=82.4  (Good)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Running Tests Locally

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=aggcat --cov-report=term-missing

# Run a specific test file
pytest tests/test_infrastructure.py -v
```

Tests are also executed automatically on every push and pull request via GitHub Actions (see `.github/workflows/ci.yml`).

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