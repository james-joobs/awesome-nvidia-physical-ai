# Control a snack drawer with a virtual camera

## How it works

### Turn a camera frame into three checks

The script draws the hand, card, and obstruction into a color array that acts as the camera input. OpenCV checks three cropped regions of interest for those features. Within each crop it produces a mask of pixels inside a given BGR (blue, green, red) range. If more than 160 pixels in the card crop match the selected green range, the script sets `badge_seen` to true. [Camera input and control code](../../../labs/everyday-robots/run_story_demos.py) · [OpenCV color range masks](https://github.com/opencv/opencv/blob/4.x/doc/tutorials/imgproc/threshold_inRange/threshold_inRange.markdown)

### Connect the decision to motion

Detecting a hand activates the control rule. A visible green card or an obstruction at the slot keeps the target closure at 0. With neither condition, the target becomes 1, and the drawer moves toward it a little on each frame.

| Trace field | How to interpret it |
| --- | --- |
| `badge_seen`, `slot_occupied` | Card and obstruction decisions from the image. The same green card yields the same decision for different people. |
| `drawer_closed_fraction` | Closure from 0 (open) to 1 (closed). |
| `drawer_final_m` | Final slide distance in the [saved scene results](../../../labs/everyday-robots/recorded.json). The run with no card and a clear slot moves about 0.305 m. |

The same pattern appears elsewhere in the collection. The cart uses passage width as input, and the desk cleanup uses a rule for what to keep or discard. Change one relevant input and observe which decision changes.

## Run it

### 1. Watch the drawer in Isaac Sim

Open the [snack drawer USD](../../../labs/everyday-robots/snack-guard.usda) via **File → Open**. Switch to **FilmCamera** and press **Play**. Watch how the drawer moves when a card is present or an object blocks the slot.

### 2. Generate a decision log on your computer

From this repository in a terminal, prepare Python and FFmpeg. Check that `command -v ffmpeg` prints a path, then run the block. This step runs on a CPU.

```sh
python3 -m venv .venv-desk
source .venv-desk/bin/activate
python -m pip install numpy opencv-python-headless
python labs/everyday-robots/run_story_demos.py ./runs/stories "$(command -v ffmpeg)"
```

Open `runs/stories/28-snack-guard/result/result.json` in a text editor. `badge_seen` means the card was visible, `slot_occupied` means the slot was blocked, and `drawer_closed_fraction` tells you how far it closed.

### 3. Try another scene

Open the [alarm](../../../labs/everyday-robots/runaway-alarm.usda), [cleanup](../../../labs/everyday-robots/desk-cleanup.usda), or [cart](../../../labs/everyday-robots/cart-clearance.usda) the same way. Keep the cart’s `workbench-asset.usda` beside its stage. To regenerate stages, use Isaac Sim Python for [drawer physics](../../../labs/everyday-robots/physics.py) and [cleanup](../../../labs/everyday-robots/desk_cleanup.py), or Python with `usd-core` for the [aisle check](../../../labs/everyday-robots/aisle.py).

## Check the result

The reversing alarm crossed the edge; the edge-aware mode stayed on top. Only the no-card case closed the drawer by about 30.5 cm. The selective cleanup put the snack in the bin and left the mouse and cup on the desk. The 55 cm and 75 cm aisles fail the 80 cm clearance rule, while the 95 cm aisle passes. [Recorded results](../../../labs/everyday-robots/recorded.json)
