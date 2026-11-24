"""R28 (task t5) generator package.

Modules
-------
``constants``      frozen paths, versions, record schema, dose semantics
``canonical``      deterministic serialisation / digests
``solver_bridge``  read-only bridge to the frozen ``vett_r25.solver`` (pinned digest)
``config``         validated build config (N, quotas, blocks, prompt budget)
``record_space``   stratified targeted enumeration of reachable records
``derivation``     solver-equivalent staged derivation with mechanical ablation
``doses``          D1-D4 real renderers (revision chain, authority conflicts, ...)
``render``         neutral prose, identity chains, question text, token estimate
``certificates``   evidence necessity, rule path, replay, authority decision
``assignment``     2^4 factor core + 4x3 dose ladder with per-layer quotas
``build``          dual rendering, twin identity, end-to-end replay
``reports``        derivation/mechanism/dose witnesses, quota report, manifest
``verify``         R26.15 zero drift and hard acceptance HA1-HA18
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

__all__ = ["__version__"]
__version__ = "1.0.0"
