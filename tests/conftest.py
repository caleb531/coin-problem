import sys
from pathlib import Path
from typing import Optional

import pytest

# For some reason, the coinproblem module does not exist on sys.path in the
# pytest context, so we must add it manually
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(
    report: pytest.TestReport, config: pytest.Config
) -> Optional[tuple[str, str, str]]:
    if report.passed and report.when == "call":
        # Silence the dot progress output for successful tests
        return report.outcome, "", report.outcome.upper()
    return None
