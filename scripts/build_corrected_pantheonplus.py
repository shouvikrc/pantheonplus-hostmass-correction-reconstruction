#!/usr/bin/env python3
"""Build an independently reconstructed host-mass-corrected Pantheon+ table.

The only scientific input is the public Pantheon+SH0ES.dat table. The
implementation follows Appendix F of Hoyt et al. (2026), arXiv:2601.19424.
No privately supplied corrected table is read or required.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd


VERSION = "1.0.0"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = REPOSITORY_ROOT / "data" / "Pantheon+SH0ES.dat"
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "data"
    / "Pantheon+SH0ES_HostMassCorrected_Reconstructed.dat"
)
DEFAULT_AUDIT = REPOSITORY_ROOT / "data" / "reconstruction_audit.csv"
DEFAULT_MANIFEST = REPOSITORY_ROOT / "data" / "reconstruction_manifest.json"
PUBLIC_INPUT_SHA256 = (
    "1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8"
)
REQUIRED_COLUMNS = {
    "CID",
    "zCMB",
    "c",
    "HOST_LOGMASS",
    "biasCor_m_b",
    "m_b_corr",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--allow-noncanonical-input",
        action="store_true",
        help="Allow an input whose SHA-256 differs from the archived public table.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.input.resolve()
    output = args.output.resolve()
    source_hash = sha256(source)

    if source == output:
        raise ValueError("Input and output paths must be different")
    if source_hash != PUBLIC_INPUT_SHA256 and not args.allow_noncanonical_input:
        raise ValueError(
            "Input SHA-256 does not match the archived public Pantheon+ table. "
            "Use --allow-noncanonical-input only after auditing the differences."
        )

    frame = pd.read_csv(source, sep=r"\s+", dtype={"CID": str})
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if len(frame) != 1701:
        raise ValueError(f"Expected 1701 Pantheon+ rows; found {len(frame)}")

    # The 713/114 counts reported in Appendix F identify the full selection:
    # 0.01 <= zCMB < 0.15, then 9.4 <= log10(M*/Msun) < 10 for affected hosts.
    low_redshift = frame["zCMB"].ge(0.01) & frame["zCMB"].lt(0.15)
    low_mass = low_redshift & frame["HOST_LOGMASS"].lt(10.0)
    high_mass = low_redshift & frame["HOST_LOGMASS"].ge(10.0)
    affected = (
        low_redshift
        & frame["HOST_LOGMASS"].ge(9.4)
        & frame["HOST_LOGMASS"].lt(10.0)
    )

    counts = {
        "all_rows": int(len(frame)),
        "low_redshift_rows": int(low_redshift.sum()),
        "low_mass_fit_rows": int(low_mass.sum()),
        "high_mass_fit_rows": int(high_mass.sum()),
        "corrected_rows": int(affected.sum()),
    }
    expected = {"low_redshift_rows": 713, "corrected_rows": 114}
    for key, expected_value in expected.items():
        if counts[key] != expected_value:
            raise ValueError(
                f"Selection check failed: {key}={counts[key]}, "
                f"expected {expected_value}"
            )

    # The two published bias-correction curves are numerically reproduced by
    # separate unweighted global cubic fits below and above the mass step.
    low_coefficients = np.polyfit(
        frame.loc[low_mass, "c"],
        frame.loc[low_mass, "biasCor_m_b"],
        deg=3,
    )
    high_coefficients = np.polyfit(
        frame.loc[high_mass, "c"],
        frame.loc[high_mass, "biasCor_m_b"],
        deg=3,
    )

    color = frame.loc[affected, "c"].to_numpy(dtype=float)
    low_curve = np.polyval(low_coefficients, color)
    high_curve = np.polyval(high_coefficients, color)
    correction = low_curve - high_curve

    corrected_magnitude = frame["m_b_corr"].to_numpy(dtype=float).copy()
    affected_positions = np.flatnonzero(affected.to_numpy())
    corrected_magnitude[affected_positions] += correction

    audit = frame.loc[
        affected,
        ["CID", "zCMB", "c", "HOST_LOGMASS", "biasCor_m_b", "m_b_corr"],
    ].copy()
    audit.insert(0, "row_index_zero_based", affected_positions)
    audit["low_mass_curve"] = low_curve
    audit["high_mass_curve"] = high_curve
    audit["delta_m_b_corr"] = correction
    audit["m_b_corr_reconstructed"] = corrected_magnitude[affected_positions]

    raw_lines = source.read_text(encoding="utf-8").splitlines()
    if len(raw_lines) != len(frame) + 1:
        raise ValueError("Parsed row count does not match the text file")
    header = raw_lines[0].split()
    magnitude_index = header.index("m_b_corr")
    affected_set = set(affected_positions.tolist())
    output_lines = [raw_lines[0]]
    for row_index, line in enumerate(raw_lines[1:]):
        if row_index not in affected_set:
            output_lines.append(line)
            continue
        fields = line.split()
        fields[magnitude_index] = repr(float(corrected_magnitude[row_index]))
        output_lines.append(" ".join(fields))

    output.parent.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    audit.to_csv(args.audit, index=False, float_format="%.17g")

    manifest = {
        "schema_version": 1,
        "builder_version": VERSION,
        "method_reference": "Hoyt et al. 2026, arXiv:2601.19424, Appendix F",
        "method": {
            "low_redshift_selection": "0.01 <= zCMB < 0.15",
            "mass_step": "HOST_LOGMASS = 10.0",
            "corrected_host_selection": "9.4 <= HOST_LOGMASS < 10.0",
            "curve_fit": "separate unweighted numpy.polyfit degree-3 fits",
            "update": (
                "m_b_corr_new = m_b_corr_public "
                "+ low_mass_curve(c) - high_mass_curve(c)"
            ),
        },
        "files": {
            "input": {
                "path": repository_path(source),
                "sha256": source_hash,
            },
            "output": {
                "path": repository_path(output),
                "sha256": sha256(output),
            },
            "audit": {"path": repository_path(args.audit)},
        },
        "counts": counts,
        "coefficients_descending_power": {
            "low_mass": low_coefficients.tolist(),
            "high_mass": high_coefficients.tolist(),
            "low_minus_high": (low_coefficients - high_coefficients).tolist(),
        },
        "correction_mag": {
            "mean_over_114_corrected_rows": float(np.mean(correction)),
            "median_over_114_corrected_rows": float(np.median(correction)),
            "minimum": float(np.min(correction)),
            "maximum": float(np.max(correction)),
            "sum_divided_by_713_low_redshift_rows": float(
                np.sum(correction) / low_redshift.sum()
            ),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {repository_path(output)}")
    print(f"Corrected rows: {counts['corrected_rows']}")
    print(f"Mean m_b_corr update: {np.mean(correction):.12f} mag")
    print(f"Output SHA-256: {sha256(output)}")


if __name__ == "__main__":
    main()
