"""Developer tool: append evidence after successful phase acceptance."""

import argparse
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument("phase", type=int)
p.add_argument("--implemented", required=True)
p.add_argument("--tests", required=True)
p.add_argument("--problems", default="无新增阻塞。")
p.add_argument("--fixes", default="无。")
p.add_argument("--validation", required=True)
a = p.parse_args()
with Path("development_log.md").open("a") as f:
    f.write(
        f"\n## Phase {a.phase}\n\nStatus: PASS\n\nImplemented:\n- {a.implemented}\n\nTests:\n- {a.tests}\n\nProblems Found:\n- {a.problems}\n\nFixes:\n- {a.fixes}\n\nValidation:\n- {a.validation}\n\nNext:\n"
        + (f"Phase {a.phase + 1}\n" if a.phase < 30 else "V1 delivery\n")
    )
git = "/Library/Developer/CommandLineTools/usr/bin/git"
subprocess.run([git, "add", "."], check=True)
subprocess.run(
    [git, "commit", "-m", f"phase-{a.phase:02d}-{a.implemented.split('；')[0][:40]}"],
    check=True,
)
