# Experiments around a desk

## How it works

The alarm controller compares stopping, reversing, and turning before the desk edge. The drawer reads a green card or an obstruction using color rules on synthetic RGB frames, then drives a PhysX prismatic joint. The cleanup experiment gives selected objects an initial push. The cart compares its required clearance against three OpenUSD layouts.

## Run it

Open the [alarm](../../../labs/everyday-robots/runaway-alarm.usda), [drawer](../../../labs/everyday-robots/snack-guard.usda), [cleanup](../../../labs/everyday-robots/desk-cleanup.usda) or [cart](../../../labs/everyday-robots/cart-clearance.usda) scene in Isaac Sim, choose `/World/FilmCamera` and press **Play**. Try `/World/FallCamera` for the alarm close-up. Keep `workbench-asset.usda` next to the cart.

Use Python with NumPy, OpenCV and FFmpeg for the first command. Use the Isaac Sim Python environment for the next two commands, and Python with `usd-core` for the last.

```sh
python labs/everyday-robots/run_story_demos.py ./runs/stories "$(command -v ffmpeg)"
python labs/everyday-robots/physics.py ./runs/stories/physics ./runs/stories/28-snack-guard/result/result.json
python labs/everyday-robots/desk_cleanup.py ./runs/cleanup
python labs/everyday-robots/aisle.py labs/scene-to-data/workbench_scene.usda ./runs/aisle
```

## Check the result

The reversing alarm crossed the edge; the edge-aware mode stayed on top. Only the no-card case closed the drawer by about 30.5 cm. The selective cleanup put the snack in the bin and left the mouse and cup on the desk. The 55 cm and 75 cm aisles fail the 80 cm clearance rule, while the 95 cm aisle passes. [Recorded results](../../../labs/everyday-robots/recorded.json)
