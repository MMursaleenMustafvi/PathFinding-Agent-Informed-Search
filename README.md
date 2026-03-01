#PathFinding-Agent Overview
A visual, grid-based pathfinding simulator that demonstrates A* and Greedy Best-First Search (GBFS) algorithms. The system supports real-time obstacle changes, automatically recalculating paths as the environment evolves.

Features

Implementation of A* and Greedy Best-First Search (GBFS)

Choice between Manhattan and Euclidean distance heuristics

Dynamic obstacle placement with automatic re-planning

Interactive grid editor:

Draw walls

Set start and goal nodes

Random maze generation (30% obstacle density)

Live performance metrics:

Number of expanded nodes

Total path cost

Execution time

Setup & Execution

Install the required library:

pip install pygame

Launch the application:

python pathfinding_agent.py
Controls
Action	Method
Set Start node	First left-click
Set Goal node	Second left-click
Draw walls	Left-click and drag
Remove node	Right-click
Start search	Click Run Search or press Space
Enable dynamic mode	Click Dynamic Mode or press D
Generate random maze	Click Random Maze or press R
Clear grid	Click Clear Board or press C
Adjust grid size	Use + / − buttons or ↑ ↓ keys
Switch algorithm	Select A* or GBFS
Switch heuristic	Choose Manhattan or Euclidean
Algorithms

A* Search
Uses the function f(n) = g(n) + h(n).
Guarantees the shortest possible path when using an admissible heuristic.

Greedy Best-First Search (GBFS)
Uses f(n) = h(n).
Often faster, but does not always produce the optimal path.
