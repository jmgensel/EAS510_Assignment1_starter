"""EAS 510 - Project 1 - Phase 2: the V2 rule set.

Rules 1-3 are kept exactly as in `rules.py`. Your job is to ADD Rule 4 that
targets the systematic weakness you diagnosed from results_v1_hard.txt.

Constraint: the rules' `out_of` weights must still sum to 100 so the Final
Score stays on a /100 scale (the format validator enforces "Final Score:
<s>/100" equals the sum of the block's rule scores).

Example split that keeps the original spirit: Rules 1-3 -> 25/25/40 and
Rule 4 -> 10 (or trim the losers more aggressively).
"""

from PIL import Image
import imagehash
import rules

#: Import the original rules and append your new one.
RULES = rules.RULES + ("rule4_edges",)

import time

def _phash(target, input_path):
  bestMatch = 0.0
  with Image.open(target["path"]) as t:
    ti = t.convert("RGB")
    th = imagehash.phash(ti)
  
  with Image.open(input_path) as i:
    ii = i.convert("RGB")

  # Try different crop sizes
  for crop in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5):
    cropw = int(ii.width * crop)
    croph = int(ii.height * crop)

    # Slide crops
    sx = max(1, cropw)
    sy = max(1, croph)
    xs = list(range(0, ii.width - cropw + 1, sx))
    ys = list(range(0, ii.height - croph + 1, sy))

    if not xs or xs[-1] != ii.width - cropw:
      xs.append(ii.width - cropw)
    if not ys or ys[-1] != ii.height - croph:
      ys.append(ii.height - croph)
    
    for x in xs:
      for y in ys:
        c = ii.crop((x, y, x+cropw, y+croph))
        tryhash = imagehash.phash(c)
        d = th - tryhash
        similarity = 1.0 - d / 64.0
        bestMatch = max(bestMatch, similarity)
  return bestMatch

def rule4_edges(target, input_path):
    """TODO: replace with your Phase 2 rule that fixes the V1 weakness.

    Starter returns a no-op so the pipeline still runs before you implement it.
    Parity with rules.py rule dict: rule/name/fired/score/out_of/note/metric.
    
    Weaknesses identified:
      1. Metadata has too strong of an impact on matching; nonmatching metadata should not cause a 30 point loss.
        -> Reduce to 15 points.
      2. Rule 4 still does not have enough space to impact score.
        -> Reduce Template rule from 40 to 30 points.
      3. Crop + resize or compress consists of most rejections.
        -> Reduction of metadata score will on its own partially fix this.
        -> Implement rule 4 to catch these issues.
        -> Research suggests phash may help with this.
          - Try different crops of the target.
          - Compare phashes and match with the best crop.
          - Fire based on best phash match.
    """
    out = {
        "rule": 4,
        "name": "PHash",
        "fired": False,
        "score": 0,
        "out_of": 25,
        "note": "PHash Similarity",
        "metric": 0.0,
      }
    similarity = _phash(target, input_path)
    out["metric"] = round(similarity, 3)
    if similarity >= 0.5:
      out["fired"] = True
      out["score"] = int(round(out["out_of"] * similarity))
    return out