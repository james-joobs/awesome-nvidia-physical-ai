# Control a snack drawer with a virtual camera

## How it works

The snack drawer **sees, decides, then moves**. A synthetic camera captures the area in front of the drawer. OpenCV looks for colors in specific parts of the image to detect the card and an obstruction. Its decision drives a joint that slides in one direction. The alarm and cart use similar rules with different inputs, such as hand distance or aisle width.

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
