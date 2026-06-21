# Reports defaults

# Number of results shown per section by default (overridden by --all)
DEFAULT_TOP_N: int = 10

# Cyclomatic Complexity (Lizard) 
# Based on McCabe's scale:
#   1–10 -> simple, low risk
#   11–20 -> moderate complexity
#   21+ > high risk, hard to test

CC_LOW: int = 10 # green threshold
CC_HIGH: int = 20 # yellow -> red threshold

# Maintainability Index (Radon)
# Scale: 0–100 (higher is better)
# 80–100 -> A (good)
# 60–79 -> B (moderate)
# 40–59 -> C (needs attention)
# 0–39 -> D (critical)

MI_GRADE_A: float = 80.0
MI_GRADE_B: float = 60.0
MI_GRADE_C: float = 40.0

# Truck factor
# Files with fewer unique authors than this threshold are considered at risk.

TRUCK_FACTOR_CRITICAL: int = 1 # red: only 1 author
TRUCK_FACTOR_WARNING: int = 2 # yellow: 2 authors

# Code Churn
# Number of commits touching a file to be considered "high churn".

CHURN_LOW: int = 10
CHURN_HIGH: int = 30

# Security (Bandit)
# Severity levels returned by Bandit and pip-audit.

SEVERITY_HIGH: str = "HIGH"
SEVERITY_MEDIUM: str = "MEDIUM"
SEVERITY_LOW: str = "LOW"

# Documentation (Cloc)
# Minimum comment ratio (comments / total lines) to avoid a documentation penalty.

MIN_COMMENT_RATIO: float = 0.10   # 10% of lines should be comments

# Dead Code (Vulture)
# Minimum confidence score (0–100) for Vulture to report unused code.

VULTURE_MIN_CONFIDENCE: int = 80