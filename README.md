# Reconstructed host-mass correction for Pantheon+

This repository independently reconstructs the corrected Pantheon+ standardized
magnitudes described in Appendix F of Hoyt et al. (2026). The reconstruction
uses only the public Pantheon+ table and does not read, copy, or require a
privately supplied corrected file.

The corrected data file can be used to verify the results in [arXiv: 2607.24443](https://arxiv.org/abs/2607.24443).

## Contents

```text
data/Pantheon+SH0ES.dat
    Unmodified public Pantheon+SH0ES table.

data/Pantheon+SH0ES_HostMassCorrected_Reconstructed.dat
    Independently generated corrected table.

data/reconstruction_audit.csv
    Row-by-row audit for the 114 corrected entries.

data/reconstruction_manifest.json
    Input/output hashes, selections, coefficients, counts, and software versions.

scripts/build_corrected_pantheonplus.py
    Complete public-input-only reconstruction.
```

## Scientific provenance

The original data vector is the public `Pantheon+SH0ES.dat` file from the
[Pantheon+SH0ES DataRelease](https://github.com/PantheonPlusSH0ES/DataRelease).
The host-mass revision and the corresponding bias-correction prescription were
introduced in Appendix F of [Hoyt et al. (2026),
arXiv:2601.19424](https://arxiv.org/abs/2601.19424). This repository provides an
independent implementation and generated derivative; it does not claim
authorship of the underlying Pantheon+ data or of the correction method.

The public Pantheon+ data documentation identifies the associated Pantheon+
analysis as [arXiv:2202.04077](https://arxiv.org/abs/2202.04077) and the SH0ES
analysis as [arXiv:2112.04510](https://arxiv.org/abs/2112.04510). These works and
Hoyt et al. 2026 [arXiv:2601.19424](https://arxiv.org/abs/2601.19424)  and Roy Choudhury 2026 [arXiv: 2607.24443](https://arxiv.org/abs/2607.24443).
should be cited when using the reconstructed table.

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
corrected rows is `+0.07220464502818282` mag. With the opposite distance-shift
sign convention used in Hoyt et al., this corresponds to their rounded
`Delta mu = -0.073 mag` statement.

## Reproduce the corrected table

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_corrected_pantheonplus.py
```

The script verifies the SHA-256 and row count of the public input, reconstructs
the corrected table, and rewrites the audit and manifest. The expected output
is:

```text
Corrected rows: 114
Mean m_b_corr update: 0.072204645028 mag
Output SHA-256: 9e17f8d5b8188016eda0ded6a9e080f94263eb2ea1457d764934084137574b13
```

Run the repository checksum audit with:

```bash
shasum -a 256 -c checksums.sha256
```

## Comparison with the supplied Hoyt table

The reconstruction script does not read or use the privately supplied Hoyt table. A separate numerical comparison was used only to validate the public-input reconstruction; the supplied table is not included in this repository and is not an input to the builder.

The post-generation comparison found:

- the same 114 corrected row positions;
- an RMS difference of `3.72e-16` mag in `m_b_corr`;
- a maximum absolute difference of `3.55e-15` mag;
- no differences in any other numerical column at `1e-12` tolerance.

Thus, the correction is independently reproduced to floating-point precision.
This repository's file deliberately retains the official CIDs from the public
Pantheon+ table. Relative to one supplied by Taylor Hoyt, the only label differences
are:

| Public CID retained here | CID in that supplied file |
|---|---|
| `1994DRichmond` | `1994D` |
| `2005df_ANU` | `2005df` |
| `2008fv_comb` | `2008fv` |


## Licensing

The independently created correction data, reconstruction software, metadata,
validation products, and documentation are released under CC BY 4.0; see
`LICENSE`. The external public Pantheon+ input retains its original ownership
and terms; see `NOTICE.md`. The associated Zenodo deposit does not redistribute
that external input. The derived table must retain attribution to both the
Pantheon+ source data and the Hoyt et al. correction method.
