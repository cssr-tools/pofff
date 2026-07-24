# SPDX-FileCopyrightText: 2025-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Reproduce Table 9 in the pofff paper:
Accuracy vs wall-time trade-offs for CNV solver tolerances.
"""

import subprocess
from pathlib import Path

from mako.template import Template
from opm.io.ecl import ESmry as OpmSummary

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

CASES = ("relax", "tight")
CNV_TOLERANCES = ("1e-2", "1e-3")
CNV_TOLERANCES_RELAXED = ("1", "1e-3")

OUTPUT_DIR = Path("accuracy")
TEMPLATE_FILE = "appendixc.mako"

# Mass injection rates × injection periods (unchanged)
CO2_REFERENCE = 3e-7 * 8100 + 2 * 3e-7 * 10200


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def run_pofff(case: str) -> None:
    """Run pofff for a given case."""
    subprocess.run(
        [
            "pofff",
            "-i",
            f"{case}.toml",
            "-o",
            case,
            "-m",
            "single",
            "-t",
            "24,48,72,96,120",
            "-f",
            "none",
        ],
        check=True,
    )


def write_case_toml(case: str, cnv: str, cnv_relaxed: str) -> None:
    """Render and write the TOML input file for a case."""
    template = Template(filename=TEMPLATE_FILE)
    rendered = template.render(
        cores=1,
        rng=7,
        cnv=cnv,
        cnv_relaxed=cnv_relaxed,
    )

    Path(f"{case}.toml").write_text(rendered, encoding="utf8")


def read_results(case: str) -> tuple[float, float]:
    """Read wall time and injected mass from OPM summary."""
    summary = OpmSummary(f"{case}/{case.upper()}.SMSPEC")
    tcpu = summary["TCPU"][-1]
    fgmip = summary["FGMIP"][-1]
    return tcpu, fgmip


# -----------------------------------------------------------------------------
# Main workflow
# -----------------------------------------------------------------------------


def main() -> None:
    """Main entry point for Table 9 in the pofff paper."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    report_lines = ["Case                         Accuracy (%)  Wall time (s)\n"]

    for case, cnv, cnv_relaxed in zip(CASES, CNV_TOLERANCES, CNV_TOLERANCES_RELAXED):
        write_case_toml(case, cnv, cnv_relaxed)
        run_pofff(case)

        tcpu, fgmip = read_results(case)

        accuracy = 100.0 * (1.0 - abs(fgmip - CO2_REFERENCE) / CO2_REFERENCE)
        report_lines.append(
            f"{case} CNV solver tolerance   " f"{accuracy:.5f}          {tcpu:.2f}\n"
        )

    (OUTPUT_DIR / "accuracy-time-trade-offs.txt").write_text(
        "".join(report_lines),
        encoding="utf8",
    )


if __name__ == "__main__":
    main()
