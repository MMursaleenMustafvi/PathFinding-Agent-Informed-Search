import pygame
import math
import random
import time
from queue import PriorityQueue

# Initialize Pygame and Fonts
pygame.init()
pygame.font.init()

# Setup Window Dimensions
WIDTH = 650
DASHBOARD_HEIGHT = 150
WIN = pygame.display.set_mode((WIDTH, WIDTH + DASHBOARD_HEIGHT))
pygame.display.set_caption("Dynamic Pathfinding Agent - AI Assignment 2")

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)         # Barrier/Walls
GREEN = (0, 255, 0)       # Final Path
RED = (255, 0, 0)         # Visited/Closed Nodes
YELLOW = (255, 255, 0)    # Frontier/Open Nodes
BLUE = (0, 0, 255)        # Goal Node
ORANGE = (255, 165, 0)    # Start Node / Agent Current Position
GREY = (200, 200, 200)    # Grid Lines
DARK_TEXT = (30, 30, 30)

# Setup Dashboard Font
STAT_FONT = pygame.font.SysFont("arial", 16, bold=True)
INFO_FONT = pygame.font.SysFont("arial", 14)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width  # Columns map to the X-axis (Horizontal)
        self.y = row * width  # Rows map to the Y-axis (Vertical)
        self.color = WHITE
        self.width = width
        self.total_rows = total_rows
        self.neighbors = []

    # Prevents Python errors if the PriorityQueue needs to compare two nodes directly
    def __lt__(self, other):
        return False

    def get_pos(self): return self.row, self.col
    def is_closed(self): return self.color == RED
    def is_open(self): return self.color == YELLOW
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == BLUE
    
    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = YELLOW
    def make_barrier(self): self.color = BLACK
    def make_end(self): self.color = BLUE
    def make_path(self): self.color = GREEN
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
        
    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # UP
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # LEFT
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

# Heuristic 1: Manhattan Distance
def h_manhattan(p1, p2):
    r1, c1 = p1
    r2, c2 = p2
    return abs(r1 - r2) + abs(c1 - c2)

# Heuristic 2: Euclidean Distance
def h_euclidean(p1, p2):
    r1, c1 = p1
    r2, c2 = p2
    return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)

# Reconstruct Final Path
def reconstruct_path(came_from, current, draw):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
        current.make_path()
        draw()
    return path

# Core Search Algorithm (Handles both A* and GBFS)
def algorithm(draw, grid, start, end, algo_type, heuristic_type):
    start_time = time.time()
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    
    # g_score tracks actual cost from start (used for Path Cost and A*)
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    
    # f_score tracks the evaluation function value
    f_score = {node: float("inf") for row in grid for node in row}
    h_start = h_manhattan(start.get_pos(), end.get_pos()) if heuristic_type == 'manhattan' else h_euclidean(start.get_pos(), end.get_pos())
    f_score[start] = h_start

    open_set_hash = {start}
    nodes_expanded = 0

    # VIVA VOCE PREPARATION: If asked to add movement weights, change this variable!
    MOVEMENT_COST = 1 

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        nodes_expanded += 1

        if current == end:
            path = reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            exec_time = (time.time() - start_time) * 1000
            final_path_cost = g_score[end] # Exact cost based on weights
            return True, nodes_expanded, final_path_cost, exec_time, path

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + MOVEMENT_COST

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                
                # Calculate Heuristic
                h_val = h_manhattan(neighbor.get_pos(), end.get_pos()) if heuristic_type == 'manhattan' else h_euclidean(neighbor.get_pos(), end.get_pos())
                
                # Apply specific algorithm logic
                if algo_type == 'gbfs':
                    f_score[neighbor] = h_val # GBFS: f(n) = h(n)
                else:
                    f_score[neighbor] = temp_g_score + h_val # A*: f(n) = g(n) + h(n)
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()

    exec_time = (time.time() - start_time) * 1000
    return False, nodes_expanded, 0, exec_time, []

# Grid Initialization
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

# Draw Grid Lines
def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

# Draw Real-Time Dashboard
def draw_dashboard(win, nodes, cost, ex_time, algo, heuri, rows):
    pygame.draw.rect(win, WHITE, (0, WIDTH, WIDTH, DASHBOARD_HEIGHT))
    pygame.draw.line(win, BLACK, (0, WIDTH), (WIDTH, WIDTH), 3)
    
    metrics_str = f"Nodes Expanded: {nodes}   |   Path Cost: {cost}   |   Time: {ex_time:.2f} ms"
    config_str = f"Algorithm: {algo.upper()}   |   Heuristic: {heuri.capitalize()}   |   Grid: {rows}x{rows}"
    
    t1 = STAT_FONT.render(metrics_str, 1, DARK_TEXT)
    t2 = STAT_FONT.render(config_str, 1, BLUE)
    
    t3 = INFO_FONT.render("[L-Click] Place Start/End/Walls   |   [R-Click] Erase", 1, BLACK)
    t4 = INFO_FONT.render("[A] A* Search   |   [G] GBFS   |   [M] Manhattan   |   [E] Euclidean", 1, BLACK)
    t5 = INFO_FONT.render("[SPACE] Start Search   |   [D] Dynamic Agent Transit Mode", 1, RED)
    t6 = INFO_FONT.render("[R] Random Maze 30%   |   [C] Clear   |   [UP/DOWN] Resize Grid", 1, BLACK)
    
    win.blit(t1, (15, WIDTH + 15))
    win.blit(t2, (15, WIDTH + 40))
    win.blit(t3, (15, WIDTH + 70))
    win.blit(t4, (15, WIDTH + 90))
    win.blit(t5, (15, WIDTH + 110))
    win.blit(t6, (15, WIDTH + 130))

# Main Render Function
def draw(win, grid, rows, width, nodes=0, cost=0, ex_time=0, algo="a*", heuri="manhattan"):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid_lines(win, rows, width)
    draw_dashboard(win, nodes, cost, ex_time, algo, heuri, rows)
    pygame.display.update()

# Get Grid coordinates from Mouse Click (FIXED)
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos  # Fixed: Proper coordinate unpacking
    col = x // gap  # X-axis is for columns
    row = y // gap  # Y-axis is for rows
    
    # Ensure clicks on the absolute right/bottom edges don't cause index out of bounds
    if row >= rows: row = rows - 1
    if col >= rows: col = rows - 1
    return row, col

# Generate Random Obstacles
def generate_random_map(grid, rows, density=0.3):
    for row in grid:
        for node in row:
            if not node.is_start() and not node.is_end():
                node.reset()
                if random.random() < density:
                    node.make_barrier()

# Dynamic Mode: Agent moving with random obstacles spawning
def dynamic_transit(draw_func, grid, path, start, end, rows, algo, heuri):
    if not path: return
    path.reverse() # Reverse to step from start to end
    current_idx = 0
    
    agent_node = start
    
    while current_idx < len(path):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Re-color previous node as path, make new node the agent (orange)
        if agent_node != start:
            agent_node.make_path()
            
        agent_node = path[current_idx]
        agent_node.make_start() # Highlight agent
        
        # Obstacle Spawning Logic (10% chance per movement step)
        if random.random() < 0.10:
            r = random.randint(0, rows-1)
            c = random.randint(0, rows-1)
            n = grid[r][c]
            
            # Ensure wall doesn't spawn on Start, End, or the Agent itself
            if n != start and n != end and n != agent_node:
                n.make_barrier()
                
                # Re-planning Mechanism: If wall obstructs remaining path
                if n in path[current_idx:]:
                    # Clear visual traces (Yellow/Red/Green) but keep Walls (Black)
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                            if node.color in [GREEN, RED, YELLOW] and node != start and node != end and node != agent_node:
                                node.reset()
                                
                    # Re-calculate path from current agent position
                    success, n_exp, p_cost, e_time, new_path = algorithm(draw_func, grid, agent_node, end, algo, heuri)
                    
                    if success:
                        return dynamic_transit(draw_func, grid, new_path, agent_node, end, rows, algo, heuri)
                    else:
                        print("Dynamic Transit Failed: Path completely blocked by new obstacle!")
                        return

        current_idx += 1
        draw_func()
        time.sleep(0.15) # Delay to visually see the agent move

def main(win, width):
    ROWS = 25
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True
    
    nodes_exp = 0
    path_cost = 0
    exec_time = 0.0
    current_algo = "a*"
    current_heuri = "manhattan"
    current_path = []

    while run:
        draw(win, grid, ROWS, width, nodes_exp, path_cost, exec_time, current_algo, current_heuri)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # LEFT CLICK: Place Start, then End, then Walls
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[1] < width: # Protect dashboard area
                    row, col = get_clicked_pos(pos, ROWS, width)
                    node = grid[row][col]
                    if not start and node != end:
                        start = node
                        start.make_start()
                    elif not end and node != start:
                        end = node
                        end.make_end()
                    elif node != start and node != end:
                        node.make_barrier()

            # RIGHT CLICK: Erase
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[1] < width:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    node = grid[row][col]
                    node.reset()
                    if node == start: start = None
                    elif node == end: end = None

            if event.type == pygame.KEYDOWN:
                # DYNAMIC GRID SIZING
                if event.key == pygame.K_UP:
                    ROWS += 5
                    grid = make_grid(ROWS, width)
                    start = None; end = None; current_path = []
                if event.key == pygame.K_DOWN and ROWS > 10:
                    ROWS -= 5
                    grid = make_grid(ROWS, width)
                    start = None; end = None; current_path = []

                # TOGGLE ALGORITHMS & HEURISTICS
                if event.key == pygame.K_a: current_algo = "a*"
                if event.key == pygame.K_g: current_algo = "gbfs"
                if event.key == pygame.K_m: current_heuri = "manhattan"
                if event.key == pygame.K_e: current_heuri = "euclidean"
                
                # RANDOM MAP EDITOR
                if event.key == pygame.K_r: 
                    generate_random_map(grid, ROWS, 0.3)
                    
                # START ALGORITHM
                if event.key == pygame.K_SPACE and start and end:
                    
                    # Clear visual nodes from previous search
                    for row in grid:
                        for node in row:
                            if node.color in [GREEN, RED, YELLOW] and node != start and node != end:
                                node.reset()
                            node.update_neighbors(grid)
                    
                    success, nodes_exp, path_cost, exec_time, current_path = algorithm(
                        lambda: draw(win, grid, ROWS, width, nodes_exp, path_cost, exec_time, current_algo, current_heuri),
                        grid, start, end, current_algo, current_heuri
                    )
                    
                # START DYNAMIC TRANSIT MODE
                if event.key == pygame.K_d and start and end and current_path:
                    dynamic_transit(
                        lambda: draw(win, grid, ROWS, width, nodes_exp, path_cost, exec_time, current_algo, current_heuri),
                        grid, current_path, start, end, ROWS, current_algo, current_heuri
                    )

                # CLEAR BOARD
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    current_path = []
                    grid = make_grid(ROWS, width)
                    nodes_exp = 0; path_cost = 0; exec_time = 0.0

    pygame.quit()

if __name__ == "__main__":
    main(WIN, WIDTH)