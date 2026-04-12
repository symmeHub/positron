# Snake Refactor Notes

## Goals

The original `snakelib.py` mixed together:

- state storage
- game rules
- handcrafted sensors
- notebook-specific experimentation

This made the code difficult to modify and slow to extend.

The refactored module separates those responsibilities and keeps two clear use cases:

- lightweight observations for genetic optimization on CPU
- optional heavier spatial helpers for debugging or future experiments

## State Representation

`FastSnake` now stores the snake as:

- one flat integer array `snake_positions`
- one scalar `snake_length`

The active snake is simply `snake_positions[:snake_length]`.

This is simpler than a full array plus an activity mask and keeps all conversions explicit.

## Main Public API

### Environment

- `FastSnake(Nrow, Ncol)`
- `reset(fix_seed=None)`
- `turn(turn_id)` with `-1 = right`, `0 = front`, `1 = left`
- `play(direction)` with absolute directions
- `simulate_turn(turn_id)`
- `simulate_direction(direction)`
- `analyze_moves()`

### Geometry helpers

- `head_position`, `tail_position`
- `head_coords`, `tail_coords`
- `snake_active_positions`
- `snake_active_coords`
- `get_neighbors_pos()`
- `get_current_direction()`

### Observation API

- `sensors(method="default")`
- `sensors(method="compact")`
- `sensors(method="local_lite")`

## Observation Families

### 1. `default`

Legacy 5-value observation kept for compatibility:

- right/front/left local content
- signed fruit direction in the snake frame

### 2. `compact`

Fixed-size vector of length 21.

For each relative action `[right, front, left]`, it includes:

- immediate safety
- whether the move eats the fruit
- reachable free-space ratio
- whether the tail remains reachable
- normalized path score to the fruit
- normalized path score to the tail

Global features appended at the end:

- continuous fruit direction in the snake frame
- normalized snake length

This representation is meant for small MLPs and is much richer than the original 5-value sensor.

### 3. `local_lite`

Head-centered local observation aligned so that the snake always moves upward.

`local_egocentric_channels_lite(radius=2)` returns 5 channels:

- walls
- body
- fruit
- tail
- region reachable from the head

With the default `radius=2`, the tensor shape is:

- `(5, 5, 5)`

Flattened through `sensors(method="local_lite")`, this gives a fixed-size vector of length:

- `125`

This is the recommended spatial starting point for a genetic TP on CPU.

## Search-Based Demonstration Agent

The module also provides:

- `RandomTurnAgent`
- `SafePathAgent`

`SafePathAgent` is not a learned controller. It is a search-based baseline used to validate the environment and the new topology helpers.

Its policy is:

1. Prefer safe fruit-seeking moves early in the game.
2. When the snake is longer, require stronger topological safety.
3. If fruit pursuit is risky, follow the tail.
4. Otherwise maximize free space and branching factor.

This is not optimal, but it is strong enough to demonstrate that:

- the new move analysis is useful
- the environment is easy to control from grid-based logic
- the classical self-wrapping failure can be pushed much farther than before

## Demo Script

Run:

```bash
python book/machine_learning/exercises/tutorials/snake_demo.py
```

Useful options:

```bash
python book/machine_learning/exercises/tutorials/snake_demo.py --rows 12 --cols 12 --episodes 20
python book/machine_learning/exercises/tutorials/snake_demo.py --agent safe --episodes 5 --max-turns 500
```

The script prints:

- observation shapes
- benchmark results for the selected agent(s)
- runtime information

## Practical Guidance

If the next goal is learning rather than heuristics:

- start with `compact` for the easiest benchmark
- try `local_lite` if you want a spatial observation that stays realistic on CPU

Heavier spatial helpers still exist in the codebase for debugging, but they are no longer part of the standard TP sensor API.
