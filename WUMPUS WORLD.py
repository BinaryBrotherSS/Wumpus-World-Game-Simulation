"""
Wumpus World Game Simulation (Hidden Map Version)
-------------------------------------------------
Standard AI environment with Fog of War logic.
The map is hidden ('?') until the agent visits a cell.

Legend:
- P: Pit (Deadly)
- W: Wumpus (Deadly, emits Stench)
- G: Gold (Goal)
- A: Agent
- B: Breeze (Adjacent to Pit)
- S: Stench (Adjacent to Wumpus)
- ?: Unknown/Unvisited area
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
        self.messages = []

    def turn_left(self):
        self.direction = (self.direction + 1) % 4
        self.messages.append(f"Turned Left. Facing: {self.get_direction_name()}")

    def turn_right(self):
        self.direction = (self.direction - 1) % 4
        self.messages.append(f"Turned Right. Facing: {self.get_direction_name()}")

    def get_direction_name(self):
        dirs = ["East", "North", "West", "South"]
        return dirs[self.direction]

    def get_forward_pos(self):
        dr, dc = 0, 0
        if self.direction == 0: dc = 1
        elif self.direction == 1: dr = 1
        elif self.direction == 2: dc = -1
        elif self.direction == 3: dr = -1
        return self.row + dr, self.col + dc

    def get_delta_direction(self):
        if self.direction == 0: return 0, 1
        elif self.direction == 1: return 1, 0
        elif self.direction == 2: return 0, -1
        elif self.direction == 3: return -1, 0


class WumpusWorld:
    def __init__(self):
        self.size = 4
        self.grid = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.agent = Agent()
        # Track visited cells for Fog of War
        self.visited = set()
        self.visited.add((0, 0)) # Start point is always visible

        self.place_objects()
        self.update_sensors()

    def place_objects(self):
        available_cells = [(r, c) for r in range(self.size) for c in range(self.size) if (r, c) != (0, 0)]

        # Gold
        gold_pos = random.choice(available_cells)
        self.grid[gold_pos[0]][gold_pos[1]] += 'G'
        available_cells.remove(gold_pos)

        # Wumpus
        wumpus_pos = random.choice(available_cells)
        self.grid[wumpus_pos[0]][wumpus_pos[1]] += 'W'
        if wumpus_pos in available_cells: available_cells.remove(wumpus_pos)

        # Pits
        for _ in range(3):
            if available_cells:
                pit_pos = random.choice(available_cells)
                self.grid[pit_pos[0]][pit_pos[1]] += 'P'
                available_cells.remove(pit_pos)

    def is_valid(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def update_sensors(self):
        # Clear sensors
        for r in range(self.size):
            for c in range(self.size):
                self.grid[r][c] = self.grid[r][c].replace('S', '').replace('B', '')

        deltas = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        for r in range(self.size):
            for c in range(self.size):
                content = self.grid[r][c]
                if 'W' in content:
                    for dr, dc in deltas:
                        nr, nc = r + dr, c + dc
                        if self.is_valid(nr, nc) and 'S' not in self.grid[nr][nc]:
                            self.grid[nr][nc] += 'S'
                if 'P' in content:
                    for dr, dc in deltas:
                        nr, nc = r + dr, c + dc
                        if self.is_valid(nr, nc) and 'B' not in self.grid[nr][nc]:
                            self.grid[nr][nc] += 'B'

    def kill_wumpus(self):
        for r in range(self.size):
            for c in range(self.size):
                if 'W' in self.grid[r][c]:
                    self.grid[r][c] = self.grid[r][c].replace('W', '')
                if 'S' in self.grid[r][c]:
                    self.grid[r][c] = self.grid[r][c].replace('S', '')
        self.agent.messages.append("SCREAM!!! You killed the Wumpus!")

    def step(self, action):
        self.agent.messages = []
        if not self.agent.is_alive: return

        if action == 'f':
            nr, nc = self.agent.get_forward_pos()
            if self.is_valid(nr, nc):
                self.agent.row, self.agent.col = nr, nc
                self.visited.add((nr, nc)) # Mark new cell as visited
                self.agent.messages.append(f"Moved to ({nr}, {nc}).")
                self.check_safety()
            else:
                self.agent.messages.append("Bump! You hit a wall.")

        elif action == 'l': self.agent.turn_left()
        elif action == 'r': self.agent.turn_right()

        elif action == 'g':
            if 'G' in self.grid[self.agent.row][self.agent.col]:
                self.agent.has_gold = True
                self.agent.messages.append("GLITTER! Found GOLD!")
                self.grid[self.agent.row][self.agent.col] = self.grid[self.agent.row][self.agent.col].replace('G', '')
            else:
                self.agent.messages.append("No gold here.")

        elif action == 's':
            if self.agent.has_arrow:
                self.agent.has_arrow = False
                self.agent.messages.append("You shot an arrow!")
                dr, dc = self.agent.get_delta_direction()
                cr, cc = self.agent.row, self.agent.col
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
        current_cell = self.grid[self.agent.row][self.agent.col]
        if 'P' in current_cell:
            self.agent.messages.append("YYYAAAHH! Fell into a Pit! (DEAD)")
            self.agent.is_alive = False
        elif 'W' in current_cell:
            self.agent.messages.append("ROAR! Eaten by Wumpus! (DEAD)")
            self.agent.is_alive = False

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display(self, reveal_all=False):
        """
        Displays the grid.
        If reveal_all is False (during game), hides unvisited cells with '?'.
        If reveal_all is True (game over), shows everything.
        """
        self.clear_screen()
        print("================ WUMPUS WORLD ================")

        h_line = " +------+------+------+------+"
        print(h_line)
        for r in range(self.size - 1, -1, -1):
            row_str = " |"
            for c in range(self.size):
                cell_content = self.grid[r][c]

                # FOG OF WAR LOGIC
                if not reveal_all and (r, c) not in self.visited:
                    # If not visited and game is running, show '?'
                    print_content = " ? "
                else:
                    # If visited OR revealing map
                    print_content = cell_content
                    # Optional: Even if visited, maybe don't show 'W' if agent is alive?
                    # But for simplicity, we show what's there if visited.
                    if print_content == '': print_content = ' '

                # Always show Agent on top if it's their position (unless dead/game over revealed)
                if r == self.agent.row and c == self.agent.col and self.agent.is_alive:
                    dirs_char = [">", "^", "<", "v"]
                    print_content = "A" + dirs_char[self.agent.direction] + print_content.replace('A', '')

                row_str += f"{print_content:^6}|"

            print(row_str)
            print(h_line)

        print("\n[STATUS REPORT]")
        print(f" Location: ({self.agent.row}, {self.agent.col})")
        print(f" Arrows: {1 if self.agent.has_arrow else 0}")

        # Percepts are ALWAYS shown for current cell
        current_content = self.grid[self.agent.row][self.agent.col]
        senses = []
        if 'B' in current_content: senses.append("BREEZE")
        if 'S' in current_content: senses.append("STENCH")
        if 'G' in current_content: senses.append("GLITTER")

        if senses: print(f" SENSES: {', '.join(senses)}")
        else: print(" SENSES: None")

        for msg in self.agent.messages:
            print(f" > {msg}")

        print("\n[CONTROLS]")
        print(" f : Forward | l : Left | r : Right")
        print(" s : Shoot   | g : Grab | q : Quit")
        print("==============================================")

# --- Main Loop ---
if __name__ == "__main__":
    game = WumpusWorld()
    game.display()

    while game.agent.is_alive:
        if game.agent.has_gold and game.agent.row == 0 and game.agent.col == 0:
            game.display(reveal_all=True) # Reveal map on win
            print("\n*** VICTORY! You escaped with the GOLD! ***")
            break

        try:
            cmd = input("Command: ").lower()
        except KeyboardInterrupt: break

        if cmd == 'q':
            print("Game Quit.")
            break
            
        game.step(cmd)

        # Check if died in this step
        if not game.agent.is_alive:
            game.display(reveal_all=True) # Reveal map on death
            print("\n*** GAME OVER ***")
        else:
            game.display(reveal_all=False) # Keep hiding
