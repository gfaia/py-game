# py-game
Collect some games

## Install

```sh
python3 -m pip install -U pygame --user
```

## Steampunk RPG demo

Run the demo from the repository root.

```sh
python3 steampunk_rpg/main.py
```

Use the arrow keys or `W`, `A`, `S`, and `D` to move one grid cell.
Use `E` beside Mechanic Ada to start or complete the task.
Use `Space` beside the clockwork sentinel to attack it.
Use `R` to start again. Use `Esc` to quit.

## Last Light survival game

Run the game from the repository root.

```sh
python3 zombie_survival/main.py
```

Use `W`, `A`, `S`, and `D` to move freely across the map.
Press `E` near a supply box or survivor.
Press `E` at the base to use medicine.
Press `B` at the base to spend four parts on a wall upgrade.
Press `N` to begin the night early.
Click to shoot zombies during the night.
Press `R` to restart or `Esc` to quit.

## Safehouse: Night Watch demo

Run the demo from the repository root.

```sh
python3 side_scroller_survival/main.py
```

Use `A` and `D` to move. Use `Space` to jump.
Press `E` near a supply crate to search it.
Aim with the mouse and click to shoot.
Press `R` to restart or `Esc` to quit.

## Linter

```sh
pip install black

black --line-length 120 .
```
