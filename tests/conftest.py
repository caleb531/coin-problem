from typing import Optional

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_report_teststatus(
    report: pytest.TestReport, config: pytest.Config
) -> Optional[tuple[str, str, str]]:
    if report.passed and report.when == "call":
        # Silence the dot progress output for successful tests
        return report.outcome, "", report.outcome.upper()
    return None
