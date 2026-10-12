"""EAS 510 - Project 1 - Phase 2: the V2 rule set.

Rules 1-3 are kept exactly as in `rules.py`. Your job is to ADD Rule 4 that
targets the systematic weakness you diagnosed from results_v1_hard.txt.

Constraint: the rules' `out_of` weights must still sum to 100 so the Final
Score stays on a /100 scale (the format validator enforces "Final Score:
<s>/100" equals the sum of the block's rule scores).

Example split that keeps the original spirit: Rules 1-3 -> 25/25/40 and
Rule 4 -> 10 (or trim the losers more aggressively).
"""

import rules

#: Import the original rules and append your new one.
RULES = rules.RULES + ("rule4_edges",)


def rule4_edges(target, input_path):
    """TODO: replace with your Phase 2 rule that fixes the V1 weakness.

    Starter returns a no-op so the pipeline still runs before you implement it.
    Parity with rules.py rule dict: rule/name/fired/score/out_of/note/metric.
    
    Weaknesses identified:
      1. Metadata has too strong of an impact on matching; nonmatching metadata should not cause a 30 point loss.
        -> Reduce to 15 points.
      2. Rule 4 still does not have enough space to impact score.
        -> Reduce Template rule from 40 to 30 points.
    """
    out = {
        "rule": 4,
        "name": "Edges",
        "fired": False,
        "score": 0,
        "out_of": 25,
        "note": "Not implemented",
        "metric": 0.0,
      }
    
    try:



    return out