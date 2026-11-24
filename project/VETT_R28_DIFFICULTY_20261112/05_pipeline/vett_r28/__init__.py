"""R28 closed-loop pipeline package (task t13).

The pipeline turns "backup -> dataset -> annotation -> judging -> metrics ->
report" into one unattended command with content-addressed caching, a gate
registry, bounded repair, degradation paths, a budget circuit breaker, a
local-first assertion and a human gate.

Entry point::

    python -m vett_r28.pipeline --config r28.toml --stage all
"""

from __future__ import annotations

import sys

# Never leave __pycache__ droppings in the R28 run tree or (worse) the frozen
# ``src/`` tree: every import below inherits this flag.
sys.dont_write_bytecode = True

__all__ = ["__version__"]
__version__ = "1.0.0"
