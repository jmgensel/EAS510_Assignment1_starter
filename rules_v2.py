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
import rules

#: Import the original rules and append your new one.
RULES = rules.RULES + ("rule4_edges",)


def _histImg(img):
    if img is None:
        return None

    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    hists = [
        cv2.calcHist([img], [i], None, [32], [0, 256])
        for i in range(3)
    ]

    hist_all = np.concatenate(hists).ravel().astype(np.float32)
    cv2.normalize(hist_all, hist_all)
    return hist_all



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
          - Compress the original image and convert to grayscale.
          - Apply Discrete Cosine Transform
          - Compare averages and fire if they are close enough.
    """
    out = {
        "rule": 4,
        "name": "PHash",
        "fired": False,
        "score": 0,
        "out_of": 25,
        "note": "Compressed and grayscale histograms.",
        "metric": 0.0,
      }
    
    try:
      # Compress the original image
      t = Image.open(target)
      b = BytesIO()
      t.save(b, format="JPEG", optimize=True, quality=40)
      b.seek(0)
        
      # Convert both images to grayscale
      t = Image.open(io.BytesIO(b))
      tg = t.convert('L')
      tb = io.BytesIO()
      tg.save(tb, format='JPEG')
      tb.seek(0)
      compressedTarget = Image.open(tb)

      i = Image.open(input_path)
      ig = i.convert('L')
      ib = io.BytesIO()
      i.save(ib, format="JPEG")
      compressedInput = Image.open(ib)

      # Re-apply histogram
      try:
        hs, hi = _histImg(compressedTarget), _histImg(compressedInput)
        if hs is None or hi is None:
            return out
        corr = float(cv2.compareHist(hs, hi, cv2.HISTCMP_CORREL))
        out["metric"] = round(max(0.0, min(1.0, corr)), 3)
        out["note"] = f"Correlation {out['metric']:.2f}"
        if out["metric"] >= 0.05:
            out["fired"] = True
            out["score"] = int(round(out["out_of"] * out["metric"]))
      except Exception:
        pass
    except Exception:
      pass  
    return out




    return out