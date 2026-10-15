# EAS 510 - Assignment 1: Digital Forensics Apprentice

A rule-based expert system that matches modified images back to their originals.

This is the **starter repository** for Project 1. Two repositories matter:

| Repository | Role |
|------------|------|
| `delveccj/EAS510_Assignment1_starter` (this repo) | Your **code** lives here. You will fork it, work in your fork, and push your final submission here. |
| `delveccj/EAS510_Assignment1` | The **dataset** (read-only). Clone it for the images; never commit it to your fork. |

## Setup on your Codio box

```bash
# 1. Fork this repo on GitHub, then in your box:
git clone https://github.com/YOUR-USERNAME/EAS510_Assignment1_starter.git
cd EAS510_Assignment1_starter

# 2. Clone the read-only dataset as a sibling folder (images live there):
cd ~/workspace
git clone https://github.com/delveccj/EAS510_Assignment1.git

# 3. Install dependencies:
cd ~/workspace/EAS510_Assignment1_starter
python3 -m pip install -r requirements.txt

# 4. Point this box at YOUR fork (run once):
./setup_git.sh
```

## Repository layout

```
forensics_detective.py   SimpleDetector: register targets + find_best_match
rules.py                 Rule functions (Rule 1: Metadata, Rule 2: Histogram, Rule 3: Template)
test_system.py           Runs the detector over the data folders and writes results_*.txt
scripts/check_output_format.py   Validates a results file against the required format
setup_git.sh, submit.sh  One-time setup + commit/push helper ("backup button")
```

## The task in one paragraph

Implement three interpretable rules (metadata, color histogram, template matching)
that combine into a 0-100 confidence score. Run your system on `modified_images/`
and `random/` and save the full output as `results_v1.txt`. In Phase 2, run on
`hard/`, diagnose a systematic failure, add a **Rule 4**, and save
`results_v1_hard.txt` and `results_v2.txt`. Full instructions are in the Codio guide
and in the assignment PDF in UBLearns.

## Running

```bash
# Phase 1 (easy + random) -> results_v1.txt
python3 test_system.py --modified --random --output results_v1.txt

# Phase 1 on hard cases -> results_v1_hard.txt
python3 test_system.py --hard --output results_v1_hard.txt

# Phase 2 (everything) -> results_v2.txt
python3 test_system.py --modified --hard --random --output results_v2.txt

# Validate any results file against the required format:
python3 scripts/check_output_format.py results_v1.txt
```

The data folders are resolved from a sibling clone of `EAS510_Assignment1`.
If your data is elsewhere, pass `--data-dir /path/to/EAS510_Assignment1`.

## Output format (do not alter)

```
Processing: modified_image_01.jpg
Rule 1 (Metadata): FIRED - Size ratio 0.85 -> 20/30 points
Rule 2 (Histogram): FIRED - Correlation 0.92 -> 25/30 points
Rule 3 (Template): FIRED - Match score 0.76 -> 30/40 points
Final Score: 75/100 -> MATCH to original_03.jpg
```

## Backup doctrine

Your Codio box can be reset at any time. **Your fork on GitHub is the only safe
copy.** After every milestone run `./submit.sh "describe what you did"`. A box
restart never touches GitHub.

## License

Apache 2.0. See `LICENSE`.

## Observed weakness in V1: what failed and why
The weakness that I observed when running the V1 rules on the hard images was a failure to match images that were cropped before being either resized or compressed.
This is because none of the V1 rules adequately checked for this combination of modifications. When a modified image was rejected:
- R1 usually wouldn't fire because the image would have been resized, which can affect metadata.
- R2 usually wouldn't fire because the crop would remove pixels from the histogram and compression removes certain details, which could remove certain pixel colors.
- R3 usually wouldn't fire because the crop would sometimes remove parts of landmarks from the image.

## Design decision for V2: what Rule 4 is and why you chose it
I decided on a phash algorithm for Rule 4 because it can compare similar images, often regardless of modification:
- Differing format is generally ignored.
- Compression is accounted for because my implementation of phash compresses both images anyways.
- Cropping is accounted for by trying different crops of the image (which is not necessarily part of the fundamental phash algorithm, but I included in my implementation).
- Brightness is partially accounted for because the distance in hashes is not as affected by uniform color changes, although brightness modifications **do** negatively impact the phash similarity score.

While implementing the rule, I had to make several changes for performance and code efficiency.
Early on, I discovered the imagehash library, which I ended up using rather than fully implementing the code manually (which was my initial approach).
One of the last changes I made was to reduce the images to a 512x512 thumbnail to make performance reasonable.

## Effect of the change: accuracy before/after on easy vs hard
Easy results (found in easy_v1.txt, easy_v2.txt):
- V1: 38/60 matched
- V2: 39/60 matched 

With V2, two previously matched images were rejected, and three previously rejected images were matched

Hard Results (found in hard_v1.txt, hard_v2.txt):
- V1: 33/60 matched
- V2: 36/60 matched

With V2, four previously matched images were rejected, and seven previously rejected images were matched

Random Results (found in random_v1.txt, random_v2.txt):
- V1: 0/15 matched; highest score 48%, average score 18.6%; all noise scores 0%
- V2: 0/15 matched; highest score 36%, average score 24.8%; noise scores similar to random scores

Ultimately, the new rule as well as the threshold and weight tweaks to scoring slightly helped with identifying both easy and hard images, and while no random images were flagged, their scores were higher on average.

## Trade-offs: what new costs or risks did Rule 4 introduce
Firstly, the most obvious cost is that Rule 4 heavily reduces performance by at least two orders of magnitude per image comparison (and each input image is compared against each target image, so this adds up quickly).
Rules 1 and 2 run in a negligible amount of time, and Rule 3 runs in about 0.0005-0.0010 seconds per comparison.
In contrast, Rule 4 can take over a second for a single comparison (although it is usually closer to 0.2 seconds per comparison).
The initial implementation of Rule 4 was even worse in this regard, often taking up to 3 seconds per comparison, which meant that a pass through all images could take upwards of 30 minutes.
To remedy this, I changed the _phash function to use a thumbnail of each image, which fortunately greatly improved performance (by reducing the data that needed to be hashed) while still firing fairly often on matching images.
One other risk introduced by Rule 4 is a higher score on non-matching images.
It was difficult to find a threshold for phash that would fire consistently on modified images but not on random images.
I settled on a threshold of 0.6 similarity score (maximum is 1.0), although I was concerned about overfitting as I experimented a bit with the values.
It is a real concern that if implemented in the real world, Rule 4 could fire often with a relatively high score on non-matching but similar images.
Finally, the V2 implementation missed some images that V1 caught, although there were more images that V1 missed but V2 caught.
This could be a concern if false negatives are particularly costly, although if that was the case, thresholds and score weights could be adjusted to improve recall at the cost of precision.
