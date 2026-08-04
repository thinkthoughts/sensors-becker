from pathlib import Path
import subprocess
import sys
import tempfile

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "generate_engineering_navigator.py"
SPEC = """\
id: absorber_manufacturing
title: Absorber Manufacturing
status: active
repository: sensors-becker
engineering_object: TES Microcalorimeter
objective: Develop a repeatable process.
current_status: Active.
depends_on:
  - detector_architecture
supports:
  - detector_module
reading_points:
  - RP_43
engineering_sessions:
  - NB_00_RP_43_SOURCE_EXTRACTION
engineering_artifacts:
  - RP_43_ENGINEERING_SESSION_REPORT
generated_figures:
  - RP_43_A
primary_sources:
  - Becker presentation
future_sources: []
current_questions:
  - What limits repeatability?
next_engineering_driver:
  - detector_module
"""

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp) / "engineering_navigator"
    driver = root / "absorber_manufacturing"
    driver.mkdir(parents=True)
    (driver / "specification.yaml").write_text(SPEC, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--write"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    output = driver / "index.md"
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "# Absorber Manufacturing" in text
    assert "RP_43" in text
    assert "generated-by: engineering-navigator-generator-v1" in text

print("generator test: PASS")
