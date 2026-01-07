"""
Wumpus World Game Simulation
----------------------------
A classic AI problem environment implemented in Python.
The Agent navigates a 4x4 grid to find Gold while avoiding Pits and the Wumpus.

Legend:
- P: Pit (Deadly)
- W: Wumpus (Deadly, emits Stench)
- G: Gold (Goal)
- A: Agent
- B: Breeze (Adjacent to Pit)
- S: Stench (Adjacent to Wumpus)
"""

import random
import os

class Agent:
    def __init__(self):
        self.row = 0
        self.col = 0
        # Directions: 0: East, 1: North, 2: West, 3: South
        self.direction = 0
        self.score = 0
        self.has_gold = False
        self.has_arrow = True
        self.is_alive = True
        self.messages = []  # Log messages for UI

    def turn_left(self):
        """Rotates the agent 90 degrees counter-clockwise."""
        self.direction = (self.direction + 1) % 4
        self.messages.append(f"Turned Left. Facing: {self.get_direction_name()}")

    def turn_right(self):
        """Rotates the agent 90 degrees clockwise."""
        self.direction = (self.direction - 1) % 4
        self.messages.append(f"Turned Right. Facing: {self.get_direction_name()}")

    def get_direction_name(self):
        """Returns the string representation of the current direction."""
        dirs = ["East", "North", "West", "South"]
        return dirs[self.direction]

    def get_forward_pos(self):
        """Calculates the coordinates of the cell in front of the agent."""
        dr, dc = 0, 0
        if self.direction == 0: dc = 1   # East
        elif self.direction == 1: dr = 1 # North
        elif self.direction == 2: dc = -1# West
        elif self.direction == 3: dr = -1# South
        return self.row + dr, self.col + dc

    def get_delta_direction(self):
        """Returns the (dr, dc) vector for the current direction (used for shooting)."""
        if self.direction == 0: return 0, 1
        elif self.direction == 1: return 1, 0
        elif self.direction == 2: return 0, -1
        elif self.direction == 3: return -1, 0


class WumpusWorld:
    def __init__(self):
        self.size = 4
        self.grid = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.agent = Agent()
        self.place_objects()
        self.update_sensors()

    def place_objects(self):
        """Randomly places Gold, Wumpus, and Pits on the grid, ensuring (0,0) is safe."""
        # Create a list of all cells except (0,0)
        available_cells = [(r, c) for r in range(self.size) for c in range(self.size) if (r, c) != (0, 0)]

        # 1. Place Gold
        gold_pos = random.choice(available_cells)
        self.grid[gold_pos[0]][gold_pos[1]] += 'G'
        available_cells.remove(gold_pos)

        # 2. Place Wumpus
        wumpus_pos = random.choice(available_cells)
        self.grid[wumpus_pos[0]][wumpus_pos[1]] += 'W'
        if wumpus_pos in available_cells: available_cells.remove(wumpus_pos)

        # 3. Place Pits (3 random pits)
        for _ in range(3):
            if available_cells:
                pit_pos = random.choice(available_cells)
                self.grid[pit_pos[0]][pit_pos[1]] += 'P'
                available_cells.remove(pit_pos)

    def is_valid(self, r, c):
        """Checks if coordinates are within the grid boundaries."""
        return 0 <= r < self.size and 0 <= c < self.size

    def update_sensors(self):
        """Updates Breeze (B) and Stench (S) indicators based on Pits and Wumpus locations."""
        # Clear existing sensors first
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.grid[r][c].replace('S', '').replace('B', '')

        deltas = [(-1, 0), (1, 0), (0, 1), (0, -1)]

        for r in range(self.size):
            for c in range(self.size):
                content = self.grid[r][c]

                # Propagate Stench around Wumpus
                if 'W' in content:
                    for dr, dc in deltas:
                        nr, nc = r + dr, c + dc
                        if self.is_valid(nr, nc) and 'S' not in self.grid[nr][nc]:
                            self.grid[nr][nc] += 'S'

                # Propagate Breeze around Pits
                if 'P' in content:
                    for dr, dc in deltas:
                        nr, nc = r + dr, c + dc
                        if self.is_valid(nr, nc) and 'B' not in self.grid[nr][nc]:
                            self.grid[nr][nc] += 'B'

    def kill_wumpus(self):
        """Removes the Wumpus and all Stench from the grid upon successful shooting."""
        for r in range(self.size):
            for c in range(self.size):
                if 'W' in self.grid[r][c]:
                    self.grid[r][c] = self.grid[r][c].replace('W', '')
                if 'S' in self.grid[r][c]:
                    self.grid[r][c] = self.grid[r][c].replace('S', '')
        self.agent.messages.append("SCREAM!!! You killed the Wumpus!")

    def step(self, action):
        """Executes one game step based on the user action."""
        self.agent.messages = [] # Clear previous messages

        if not self.agent.is_alive:
            return

        # --- MOVE FORWARD ---
        if action == 'f':
            nr, nc = self.agent.get_forward_pos()
            if self.is_valid(nr, nc):
                self.agent.row, self.agent.col = nr, nc
                self.agent.messages.append(f"Moved to ({nr}, {nc}).")
                self.check_safety()
            else:
                self.agent.messages.append("Bump! You hit a wall.")

        # --- TURN ---
        elif action == 'l': self.agent.turn_left()
        elif action == 'r': self.agent.turn_right()

        # --- GRAB GOLD ---
        elif action == 'g':
            if 'G' in self.grid[self.agent.row][self.agent.col]:
                self.agent.has_gold = True
                self.agent.messages.append("GLITTER! Found GOLD!")
                # Remove gold visually
                self.grid[self.agent.row][self.agent.col] = self.grid[self.agent.row][self.agent.col].replace('G', '')
            else:
                self.agent.messages.append("No gold here.")

        # --- SHOOT ARROW ---
        elif action == 's':
            if self.agent.has_arrow:
                self.agent.has_arrow = False
                self.agent.messages.append("You shot an arrow!")

                dr, dc = self.agent.get_delta_direction()
                cr, cc = self.agent.row, self.agent.col

                # Arrow travels until it hits a wall or the Wumpus
                while True:
                    cr += dr
                    cc += dc
                    if not self.is_valid(cr, cc):
                        self.agent.messages.append("Arrow hit the wall.")
                        break

                    if 'W' in self.grid[cr][cc]:
                        self.kill_wumpus()
                        break
            else:
                self.agent.messages.append("You have no arrows left!")

    def check_safety(self):
        """Checks if the agent has fallen into a pit or been eaten."""
        current_cell = self.grid[self.agent.row][self.agent.col]
        if 'P' in current_cell:
            self.agent.messages.append("YYYAAAHH! Fell into a Pit! (DEAD)")
            self.agent.is_alive = False
        elif 'W' in current_cell:
            self.agent.messages.append("ROAR! Eaten by Wumpus! (DEAD)")
            self.agent.is_alive = False

    def clear_screen(self):
        """Clears the console screen for a cleaner UI."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display(self):
        """Renders the game grid and status to the console."""
        self.clear_screen()
        print("================ WUMPUS WORLD ================")

        h_line = " +------+------+------+------+"
        print(h_line)
        for r in range(self.size - 1, -1, -1):
            row_str = " |"
            for c in range(self.size):
                cell_content = self.grid[r][c]

                # Render Agent with direction
                if r == self.agent.row and c == self.agent.col:
                    dirs_char = [">", "^", "<", "v"]
                    cell_content = "A" + dirs_char[self.agent.direction] + cell_content

                if cell_content == '': cell_content = ' '
                row_str += f"{cell_content:^6}|"

            print(row_str)
            print(h_line)

        # Status Report
        print("\n[STATUS REPORT]")
        print(f" Location: ({self.agent.row}, {self.agent.col})")
        print(f" Arrows: {1 if self.agent.has_arrow else 0}")

        # Display Percepts
        current_content = self.grid[self.agent.row][self.agent.col]
        senses = []
        if 'B' in current_content: senses.append("BREEZE")
        if 'S' in current_content: senses.append("STENCH")
        if 'G' in current_content: senses.append("GLITTER")

        if senses:
            print(f" SENSES: {', '.join(senses)}")
        else:
            print(" SENSES: None")

        # Game Messages
        for msg in self.agent.messages:
            print(f" > {msg}")

        # Controls
        print("\n[CONTROLS]")
        print(" f : Forward | l : Left | r : Right")
        print(" s : Shoot   | g : Grab | q : Quit")
        print("==============================================")

# --- Main Execution Block ---
if __name__ == "__main__":
    game = WumpusWorld()
    game.display()

    while game.agent.is_alive:
        # Victory Condition: Have Gold + Back at (0,0)
        if game.agent.has_gold and game.agent.row == 0 and game.agent.col == 0:
            print("\n*** VICTORY! You escaped with the GOLD! ***")
            break

        try:
            cmd = input("Command: ").lower()
        except KeyboardInterrupt:
            break

        if cmd == 'q':
            print("Game Quit.")
            break

        game.step(cmd)
        game.display()

    if not game.agent.is_alive:
        print("\n*** GAME OVER ***")
