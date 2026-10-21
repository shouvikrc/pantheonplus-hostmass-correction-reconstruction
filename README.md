# Reproduction code for the Hoyt et al. (2026, [arXiv:2601.19424](https://arxiv.org/abs/2601.19424)) Pantheon+ host-mass correction

**The authoritative release of the corrected Pantheon+ data and code is
maintained by Taylor Hoyt (Hoyt et al. 2026):
<https://github.com/tjhoyt/panplus_CorrectedLowZ>.** Please obtain the
corrected data there and cite Hoyt et al. (2026).

The current version of this repository contains the reproduction code and the
unmodified public Pantheon+ input, but no corrected data table or row-by-row
correction file. Obtain the corrected data from the Hoyt repository linked
above.

The code implements a computational reproduction of the correction
prescription described in Appendix F of [Hoyt et al. (2026),
arXiv:2601.19424](https://arxiv.org/abs/2601.19424), prepared to document the
corrected Pantheon+ input used in [Roy Choudhury (2026), ApJL, 1008,
L50](https://doi.org/10.3847/2041-8213/ae9d80)
([arXiv:2607.24443](https://arxiv.org/abs/2607.24443)).

Scientific credit for the
correction belongs to Hoyt et al. (2026), and credit for the underlying
Pantheon+ measurements belongs to their original authors.

## Contents

```text
data/Pantheon+SH0ES.dat
    Unmodified public Pantheon+SH0ES table.

scripts/build_corrected_pantheonplus.py
    Reproduction script; reads only the public Pantheon+ table.

checksums.sha256
    Checksums for the supplied public input, script, and requirements.

.gitignore
    Excludes locally generated corrected tables, audits, and manifests.
```

## Scientific provenance

The original data vector is the public `Pantheon+SH0ES.dat` file from the
[Pantheon+SH0ES DataRelease](https://github.com/PantheonPlusSH0ES/DataRelease).
The host-mass revision and the corresponding bias-correction prescription were
introduced in Appendix F of [Hoyt et al. (2026),
arXiv:2601.19424](https://arxiv.org/abs/2601.19424). This repository is a
reproduction of that prescription; it does not claim authorship of the
underlying Pantheon+ data or of the correction.

Users of the corrected magnitudes should cite Hoyt et al. (2026)
[arXiv:2601.19424](https://arxiv.org/abs/2601.19424) and the Pantheon+ and
SH0ES papers: [arXiv:2112.03863](https://arxiv.org/abs/2112.03863),
[arXiv:2202.04077](https://arxiv.org/abs/2202.04077), and
[arXiv:2112.04510](https://arxiv.org/abs/2112.04510).

## Reconstruction

The two counts stated by Hoyt et al., 713 low-redshift rows and 114 affected
rows, are recovered exactly using

```text
0.01 <= zCMB < 0.15
```

and

```text
9.4 <= HOST_LOGMASS < 10.0.
```

The redshift is therefore the cosmic-microwave-background-frame column `zCMB`,
including the lower bound at 0.01.

For all 713 selected rows, the script fits `biasCor_m_b` as a function of the
SALT color parameter `c` separately below and above the host-mass step at
`HOST_LOGMASS = 10`. The published curves are numerically reproduced by two
unweighted global cubic fits. Their difference is

```text
delta_m_b_corr(c) = low_mass_curve(c) - high_mass_curve(c)
                  = -2.329137438480565 c^3
                    +1.424528256365359 c^2
                    +0.5989960990241795 c
                    +0.06336434683780452.
```

For each of the 114 affected rows,

```text
m_b_corr_new = m_b_corr_public + delta_m_b_corr(c).
```

No other field is changed. In particular, this procedure does not alter
`biasCor_m_b`, the redshift columns, light-curve parameters, uncertainties, or
the public covariance matrices. The average file-level change among the 114
corrected rows is `+0.07220464502818282` mag.

## Run the reproduction locally

For the original corrected data and the authors' implementation, use
[Hoyt et al.'s repository](https://github.com/tjhoyt/panplus_CorrectedLowZ).
The following commands are provided for checking this reproduction locally;
their generated outputs are not distributed in the current repository version.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_corrected_pantheonplus.py
```

The script verifies the SHA-256 and row count of the public input, then writes
the following local outputs under `data/`:

- `Pantheon+SH0ES_HostMassCorrected_Reconstructed.dat`: reconstructed table.
- `reconstruction_audit.csv`: row-by-row correction audit.
- `reconstruction_manifest.json`: hashes, selections, coefficients, and counts.

These three files are ignored by Git and are not included in
`checksums.sha256`. The expected terminal output is:

```text
Corrected rows: 114
Mean m_b_corr update: 0.072204645028 mag
Output SHA-256: 9e17f8d5b8188016eda0ded6a9e080f94263eb2ea1457d764934084137574b13
```

Check the supplied input, script, and requirements with:

```bash
shasum -a 256 -c checksums.sha256
```

## Licensing

The reproduction code and documentation in this repository are released under
CC BY 4.0; see `LICENSE`. No ownership of, or authority to license rights held
by others in, the Hoyt et al. correction products or the Pantheon+ measurements
is asserted here. This clarification does not revoke any rights validly granted
under earlier versions of this repository's license. The external public
Pantheon+ input retains its original ownership and terms; see `NOTICE.md`.
