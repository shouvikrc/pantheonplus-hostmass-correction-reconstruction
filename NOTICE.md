# Data provenance and redistribution notice

`data/Pantheon+SH0ES.dat` is an unmodified copy of the public Pantheon+SH0ES
data vector distributed by the Pantheon+SH0ES collaboration at:

https://github.com/PantheonPlusSH0ES/DataRelease

Its SHA-256 is:

```text
1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8
```

The upstream repository did not display an explicit data or repository license
when this package was assembled on 2026-08-18. Inclusion here does not change
the ownership or terms of the upstream data. Users should retain the original
attribution, cite the Pantheon+ and SH0ES papers identified in the upstream
README, and confirm any redistribution requirements relevant to their use.

The current repository version does not distribute a corrected Pantheon+
table or a row-by-row correction file. The correction was introduced by
Hoyt et al. (2026), arXiv:2601.19424, Appendix F. Obtain the original corrected
data and code from https://github.com/tjhoyt/panplus_CorrectedLowZ and cite
Hoyt et al. (2026) when using the corrections.

`scripts/build_corrected_pantheonplus.py` is retained for local reproduction
from the unmodified public input. Its generated table, audit, and manifest
are excluded from Git tracking and are not part of the current distribution.
