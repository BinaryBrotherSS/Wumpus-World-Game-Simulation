# Wumpus World AI Simulation

A Python implementation of the classic "Wumpus World" problem from *Artificial Intelligence: A Modern Approach* (Russell & Norvig).

## Overview
This project simulates the environment where an AI agent must navigate a 4x4 grid to find Gold while avoiding deadly Pits and the Wumpus monster.

## Game Rules
- **Grid:** 4x4 layout.
- **Start:** Agent starts at coordinates (0,0).
- **Goal:** Find the Gold (G), grab it, and return to (0,0).
- **Hazards:**
  - **P (Pit):** Falling into a pit results in instant death.
  - **W (Wumpus):** Entering the Wumpus's cell results in being eaten.
- **Sensors (Percepts):**
  - **Breeze (B):** Felt in cells adjacent to a Pit.
  - **Stench (S):** Smelled in cells adjacent to the Wumpus.
  - **Glitter:** Perceived when in the same cell as the Gold.
- **Actions:**
  - **Move:** Forward, Turn Left, Turn Right.
  - **Shoot:** The agent has 1 arrow to kill the Wumpus. If the Wumpus dies, the "Stench" is removed.

## Controls
- `f` : Move Forward
- `l` : Turn Left
- `r` : Turn Right
- `g` : Grab Gold
- `s` : Shoot Arrow
- `q` : Quit Game

## How to Run
1. Ensure you have Python installed.
2. Run the script:
   ```bash
   python wumpus_world.py
