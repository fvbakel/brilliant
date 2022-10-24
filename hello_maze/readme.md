# Maze datamodels

## Overview of Modules

```mermaid
  graph TD;
    BaseGrid --> Maze
    BaseGrid --> GameGrid
    GameGrid --> Maze
    Graph  --> Maze
    Maze --> Maze_GUI
    Maze --> MazeTextUI

```

## BaseGrid

```mermaid
  classDiagram

    class Position {
        col : int
        row : int
        get_direction(Position)
        is_neighbor(Position)
    }

    class Route {
        _path : list[Position]
        add_route(Route)
        has_position(Position)
        append(Position)
        is_valid()
    }
    Route --> Position

    class Size {
        nr_of_cols : int
        nr_of_rows : int
    }

    class Direction {
        <<Enumeration>>
        LEFT
        RIGHT
        UP
        DOWN
        HERE
    }

    class Orientation {
        <<Enumeration>>
        HORIZONTAL
        VERTICAL
    }

    Grid "Position" -->  Any
    Grid --> Size

    class Grid {
        size : Size
        get_location(Position | (col,row))
        set_location(Position | (col,row),content)
    }


```


## Graph

```mermaid
  classDiagram

    class Graph {
        is_fully_connected()
        is_recursive()
        get_shortest_path()
        get_node(id:str) Node
    }
    class Node {
        visited : bool
        id : str
    }
    class Edge {
        active : bool
    }
    class EdgePair {
        enable()
        disable()
    }

    Graph  --> Node : nodes
    Graph -->  Edge : edges
    Graph -->  EdgePair : pairs
    
    Node  -->  Edge : child edges
    Node  -->  Edge : parent edges

    Edge  -->  Node : parent
    Edge  -->  Node : child

    EdgePair "1" --> "2" Edge


```
## GameGrid


```mermaid
  classDiagram
    class Material {
        <<Enumeration>>
        NONE
        FLOOR
        STONE
        PLASTIC
        ...
    }

    class GameContent {
        solid : bool
        mobile : bool
        
    }
    class GameGrid {
        
    }

    GameGrid <|-- BaseGrid

    GameGrid "Position" -->  GameContent
    GameContent --> Position
    GameContent --> GameContent : guest
    GameContent --> Material


    class Floor {
    }
    class Wall {
    }
    class Particle {
    }
    

    Floor <|-- GameContent
    Wall <|-- GameContent
    Particle <|-- GameContent

    GameGridRender --> GameGrid
    ImageGameGridRender <|-- GameGridRender
    TextGameGridRender <|-- GameGridRender
    
    class ActionControl {
        game_grid: GameGrid
        do_one_cycle()
    }
 
    Behavior <-- GameGrid : behaviors
    Behavior --> GameContent: subject
    ManualMove <|-- Behavior
    

```

## Maze

```mermaid
  classDiagram
    class MazeGame {
        square_size:Size
        game_size:Size
        wall_width:int
    }


    Graph  --> Node : nodes
    Node --> Edge
    EdgePair --> Edge 
    Graph --> EdgePair

    class Square {
        
    }

    class MazeGenerator {
        generate(Size) Maze
    }




    Maze --> Graph
    MazeGame --> Maze
    MazeGame --> SquareGeometryGrid
    MazeGame --> GameGrid
    SquareGeometryGrid --> SquareGeometry : position
    Maze --> SquareGrid
    

    SquareGrid "Position" -->  Square
    Square --> Node
    Square --> EdgePair : Direction

    GameGrid --> GameContent : position

```

### Maze Behavior

```mermaid
    classDiagram
    class MoveInfo {
        start_pos : Position
        available_hosts : dict[Direction,GameContent]
        available_positions : set[Position]
        all_positions : set[Position]
        has_available()
        get_random_available(set[Position])
    }

    class AutomaticMove {
        nr_stand_still : int
    }

    AutomaticMove <|-- Behavior

    AutomaticMove --> Route : history
    AutomaticMove --> MoveInfo

    RandomMove <|-- AutomaticMove
    RandomDistinctMove <|-- AutomaticMove
    RandomCommonMove <|-- AutomaticMove
    MoveBack  <|-- AutomaticMove

    BlockDeadEnds  <|-- MoveBack
    BackOut <|-- BlockDeadEnds

    Spoiler <|-- BlockDeadEnds

    StateMove  <|-- AutomaticMove

```

### Maze Behavior State Machine

```mermaid
    classDiagram
    class MoveInfo {
        start_pos : Position
        available_hosts : dict[Direction,GameContent]
        available_positions : set[Position]
        all_positions : set[Position]
        has_available()
        get_random_available(set[Position])
    }

    class AutomaticMove {
        nr_stand_still : int
    }

    AutomaticMove <|-- Behavior

    AutomaticMove --> Route : history
    AutomaticMove --> MoveInfo

    RandomMove <|-- AutomaticMove
    RandomDistinctMove <|-- AutomaticMove
    RandomCommonMove <|-- AutomaticMove
    MoveBack  <|-- AutomaticMove

    BlockDeadEnds  <|-- MoveBack
    BackOut <|-- BlockDeadEnds

    Spoiler <|-- BlockDeadEnds

```

#### Options

**Option 1:** Separate states for start end end in cycle

**Option 2:** One state handles start and end cycle

```mermaid
stateDiagram-v2
    [*] --> Start
    
    Start --> WaitNextCycle
    WaitNextCycle --> StartCycle
    StartCycle --> RandomMove
    StartCycle --> FollowPath
    RandomMove --> WaitNextCycle
    FollowPath --> WaitNextCycle
    StandStill --> WaitNextCycle
    WaitNextCycle --> Finished
    
    Finished --> [*]
```

```mermaid
stateDiagram-v2
    [*] --> Start
    
    Start --> NewMove
    NewMove --> MoveStopped
    MoveStopped --> ChooseTarget
    NewMove --> DeadEnd
    DeadEnd --> ChooseTarget
    ChooseTarget --> FollowPath
    FollowPath --> NewMove
    NewMove --> FollowPath
    

    NewMove --> RandomMove
    RandomMove --> NewMove

    NewMove --> Finished
    Finished --> [*]
```

### Maze Behavior Rule engine

```mermaid
flowchart LR

    subgraph Decide
        direction TB
        subgraph MoveInfo
            direction TB
            has_available --> 
            has_new_available --> 
            has_new
        end

        subgraph Router
            direction TB
            has_route
        end
        
        is_route_follow_possible -->
        is_standing_still -->
        
        has_coordinator -->
        is_following_coordinator -->
        coordinator_has_suggestion -->
        coordinator_has_new_pos -->
        coordinator_has_new_target -->
        coordinator_has_new_route  -->
        previous_action
    end

    subgraph Action
        direction TB
        subgraph Router
            direction TB
            set_route -->
            set_route_to_route --> 
            freeze_route -->
            reset_route
        end

        add_to_do_head -->
        add_to_do_tail -->
        get_next_to_do -->
        notify_coordinator
    end

    subgraph NewMove
        direction TB
        subgraph Router
            direction TB
            get_new_pos
        end
        subgraph MoveInfo
            direction TB
            get_random_available
            get_random_new_available
        end
        StandStill -->
        ClockWiseMove -->
        CoordinatedMove
    end
    
    
    Decide --> Action
    Action --> Decide
    Action --> NewMove
    Decide --> NewMove

```