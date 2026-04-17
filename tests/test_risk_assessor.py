from reliability.risk_assessor import assess_risk


def test_no_fix_is_high_risk():
    risk = assess_risk(
        original_code="print('hi')\n",
        fixed_code="",
        issues=[{"type": "Code Quality", "severity": "Low", "msg": "print"}],
    )
    assert risk["level"] == "high"
    assert risk["should_autofix"] is False
    assert risk["score"] == 0


def test_low_risk_when_minimal_change_and_low_severity():
    original = "import logging\n\ndef add(a, b):\n    return a + b\n"
    fixed = "import logging\n\ndef add(a, b):\n    return a + b\n"
    risk = assess_risk(
        original_code=original,
        fixed_code=fixed,
        issues=[{"type": "Code Quality", "severity": "Low", "msg": "minor"}],
    )
    assert risk["level"] in ("low", "medium")  # depends on scoring rules
    assert 0 <= risk["score"] <= 100


def test_high_severity_issue_drives_score_down():
    original = "def f():\n    try:\n        return 1\n    except:\n        return 0\n"
    fixed = "def f():\n    try:\n        return 1\n    except Exception as e:\n        return 0\n"
    risk = assess_risk(
        original_code=original,
        fixed_code=fixed,
        issues=[{"type": "Reliability", "severity": "High", "msg": "bare except"}],
    )
    assert risk["score"] <= 60
    assert risk["level"] in ("medium", "high")


def test_dangerous_pattern_introduced_by_fix_is_penalized():
    original = "def run(cmd):\n    return None\n"
    fixed = "import os\ndef run(cmd):\n    os.system(cmd)\n"
    risk = assess_risk(
        original_code=original,
        fixed_code=fixed,
        issues=[],
    )
    assert risk["score"] <= 70
    assert any("os.system(" in r for r in risk["reasons"])
    assert risk["should_autofix"] is False


def test_dangerous_pattern_not_penalized_if_already_in_original():
    original = "import os\ndef run(cmd):\n    os.system(cmd)\n"
    fixed = "import os\ndef run(cmd):\n    os.system(cmd)  # unchanged\n"
    risk = assess_risk(
        original_code=original,
        fixed_code=fixed,
        issues=[],
    )
    assert not any("os.system(" in r for r in risk["reasons"])


def test_missing_return_is_penalized():
    original = "def f(x):\n    return x + 1\n"
    fixed = "def f(x):\n    x + 1\n"
    risk = assess_risk(
        original_code=original,
        fixed_code=fixed,
        issues=[],
    )
    assert risk["score"] < 100
    assert any("Return" in r or "return" in r for r in risk["reasons"])


#test cleanish.py from sample_code
#import sys, os
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sample_code.cleanish import add

def test_add_function_has_no_issues():
    #ran and passed
    from bughound_agent import BugHoundAgent
    code = open("sample_code/cleanish.py").read()
    fixed = code  # No changes made
    risk = assess_risk(
        original_code=code,
        fixed_code=fixed,
        issues=[],
    )
    assert risk["score"] == 100
    assert risk["level"] == "low"

#test sample_code/flaky_try_except.py
def test_flaky_try_except_is_high_risk():
    code = open("sample_code/flaky_try_except.py").read()
    #make fixed risky by introducing a write command in th  e except block, which is a common anti-pattern that can lead to data loss or corruption
    fixed = "def load_text_file(path):\n    try:\n        f = open(path, 'r')\n        data = f.read()\n        f.close()\n    except:\n        with open('error.log', 'a') as log:\n            log.write(f'Failed to read {path}\\n')\n        return None\n\n    return data\n"
    
    risk = assess_risk(
        original_code=code,
        fixed_code=fixed,
        issues=[{"type": "Reliability", "severity": "High", "msg": "bare except"}],
    )
    assert risk["score"] <= 60
    assert risk["level"] in ("medium", "high")  


# test sample_code/mixed_issues.py
def test_mixed_issues_leads_to_low_risk():
    code = open("sample_code/mixed_issues.py").read()
    #fixed handles division by zero properly and removes the bare except, which should significantly reduce the risk score compared to the original code. 
    # However, it still doesn't check for the passed arguments types 
    # but that's a low risk overall.
    fixed = "def compute_ratio(x, y):\n    if y == 0:\n        return 0\n    return x / y\n"
    
    risk = assess_risk(
        original_code=code,
        fixed_code=fixed,
        issues=[
            {"type": "Code Quality", "severity": "Low", "msg": "missing docstring"},
            {"type": "Reliability", "severity": "High", "msg": "bare except"},
        ],
    )
    assert risk["score"] <= 100 and risk["score"] >= 80  # should be a significant improvement but not perfect
    assert risk["level"] in ("low")
