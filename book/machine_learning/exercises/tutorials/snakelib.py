from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np


DIR_RIGHT = 0
DIR_UP = 1
DIR_LEFT = 2
DIR_DOWN = 3
DIR_ORDER = (DIR_RIGHT, DIR_UP, DIR_LEFT, DIR_DOWN)

TURN_RIGHT = -1
TURN_FRONT = 0
TURN_LEFT = 1
TURN_IDS = np.array([TURN_RIGHT, TURN_FRONT, TURN_LEFT], dtype=np.int8)

DIRECTION_NAMES = {
    DIR_RIGHT: "right",
    DIR_UP: "up",
    DIR_LEFT: "left",
    DIR_DOWN: "down",
}

DIRECTION_VECTORS = {
    DIR_RIGHT: (0, 1),
    DIR_UP: (-1, 0),
    DIR_LEFT: (0, -1),
    DIR_DOWN: (1, 0),
}

ROTATION_TO_UP = {
    DIR_UP: 0,
    DIR_RIGHT: 1,
    DIR_DOWN: 2,
    DIR_LEFT: 3,
}


@dataclass(frozen=True)
class MoveAnalysis:
    turn: int
    direction: int
    status: int
    safe: bool
    eats_fruit: bool
    new_head: int
    free_space_ratio: float
    tail_reachable: bool
    fruit_path_length: float
    tail_path_length: float
    fruit_progress: float
    branching_factor: float


def pos_to_coords(pos, Ncol):
    """
    Convert flattened positions to row/column coordinates.
    """
    pos = np.asarray(pos)
    return pos // Ncol, pos % Ncol


def coords_to_pos(row, col, Ncol):
    """
    Convert row/column coordinates to flattened positions.
    """
    return np.asarray(row) * Ncol + np.asarray(col)


def get_neighbors(pos, Nrow, Ncol):
    """
    Return neighbors in the order [right, up, left, down].
    Missing neighbors are encoded with -1.
    """
    out = np.full(4, -1, dtype=np.int32)
    row = pos // Ncol
    col = pos % Ncol
    if col < Ncol - 1:
        out[DIR_RIGHT] = pos + 1
    if row > 0:
        out[DIR_UP] = pos - Ncol
    if col > 0:
        out[DIR_LEFT] = pos - 1
    if row < Nrow - 1:
        out[DIR_DOWN] = pos + Ncol
    return out


def get_Moore_neighbors(pos, Ncol):
    """
    Return the 8 Moore neighbors of a flattened position.
    """
    return np.array(
        [
            pos + 1,
            pos - Ncol + 1,
            pos - Ncol,
            pos - Ncol - 1,
            pos - 1,
            pos + Ncol - 1,
            pos + Ncol,
            pos + Ncol + 1,
        ],
        dtype=np.int32,
    )


def get_rank2_Moore_neighbors(pos, Ncol, Nrow):
    """
    Return the 24 cells of the 5x5 neighborhood centered on pos.
    Missing neighbors are encoded with -1.
    """
    row, col = pos_to_coords(pos, Ncol)
    out = []
    for drow in range(-2, 3):
        for dcol in range(-2, 3):
            if drow == 0 and dcol == 0:
                continue
            nrow = int(row) + drow
            ncol = int(col) + dcol
            if 0 <= nrow < Nrow and 0 <= ncol < Ncol:
                out.append(int(coords_to_pos(nrow, ncol, Ncol)))
            else:
                out.append(-1)
    return np.array(out, dtype=np.int32)


class FastSnake:
    """
    Snake environment with two observation families:
    - compact topology features suitable for small MLPs
    - egocentric grid observations aligned with the snake head

    The game state is stored as a flat array of positions plus a scalar length.
    This is efficient and much easier to reason about than a full-length array
    combined with a boolean activity mask.
    """

    SENSOR_SPECS = {
        "default": 5,
        "compact": 21,
        "topology": 21,
    }

    def __init__(
        self,
        Nrow,
        Ncol,
        snake_color=(0, 0, 0),
        snake_head_color=(128, 128, 128),
        forbidden_color=(255, 0, 0),
        fruit_color=(0, 255, 0),
        void_color=(255, 255, 255),
        record_turns=False,
        recorded_sensors_method="default",
        display_sensor_method=None,
    ):
        self.Nrow = int(Nrow)
        self.Ncol = int(Ncol)
        self.Ncell = self.Nrow * self.Ncol
        self.playable_cells = max(1, (self.Nrow - 2) * (self.Ncol - 2))
        self.max_manhattan_distance = max(1, (self.Nrow - 2) + (self.Ncol - 2))

        self.all_positions = np.arange(self.Ncell, dtype=np.int32)
        self.grid_values = self.all_positions.reshape(self.Nrow, self.Ncol)

        self._wall_mask = np.zeros((self.Nrow, self.Ncol), dtype=bool)
        self._wall_mask[0, :] = True
        self._wall_mask[-1, :] = True
        self._wall_mask[:, 0] = True
        self._wall_mask[:, -1] = True
        self.forbidden_positions = self.grid_values[self._wall_mask]
        self.authorized_positions = self.grid_values[~self._wall_mask]

        self._grid = np.ones((self.Nrow, self.Ncol, 3), dtype=np.uint8) * 255
        self._bfs_visited = np.zeros((self.Nrow, self.Ncol), dtype=bool)
        self._center_buffer = np.zeros((4, 2 * self.Nrow - 1, 2 * self.Ncol - 1))

        self.snake_color = snake_color
        self.snake_head_color = snake_head_color
        self.forbidden_color = forbidden_color
        self.fruit_color = fruit_color
        self.void_color = void_color

        self.record_turns = record_turns
        self.recorded_sensors_method = recorded_sensors_method
        self.display_sensor_method = display_sensor_method

        self._sensor_methods = {
            "default": self._default_sensors,
            "compact": self._compact_sensors,
            "topology": self._compact_sensors,
            "egocentric": self._egocentric_flat_sensors,
        }

        self.reset()

    def reset(self, fix_seed=None):
        """
        Reset the environment to its initial configuration.
        """
        if fix_seed is not None:
            np.random.seed(fix_seed)

        self.snake_positions = np.zeros(self.Ncell, dtype=np.int32)
        self.snake_length = 2
        self.snake_positions[0] = int(self.grid_values[1, 1])
        self.snake_positions[1] = int(self.grid_values[2, 1])

        self.status = 0
        self.score = 0
        self.iteration = 0
        self.recorded_turns = []
        self.recorded_sensors = []
        self.recorded_status = []
        self.set_fruit()

    @property
    def snake_active_positions(self):
        return self.snake_positions[: self.snake_length]

    @property
    def snake_active(self):
        out = np.zeros(self.Ncell, dtype=bool)
        out[: self.snake_length] = True
        return out

    @property
    def snake_active_coords(self):
        rows, cols = pos_to_coords(self.snake_active_positions, self.Ncol)
        return np.column_stack((rows, cols))

    @property
    def head_position(self):
        return int(self.snake_positions[0])

    @property
    def head_coords(self):
        row, col = pos_to_coords(self.head_position, self.Ncol)
        return int(row), int(col)

    @property
    def tail_position(self):
        return int(self.snake_positions[self.snake_length - 1])

    @property
    def tail_coords(self):
        row, col = pos_to_coords(self.tail_position, self.Ncol)
        return int(row), int(col)

    @property
    def free_positions(self):
        occupied = np.zeros(self.Ncell, dtype=bool)
        occupied[self.forbidden_positions] = True
        occupied[self.snake_active_positions] = True
        return self.all_positions[~occupied]

    def pos_to_coords(self, pos):
        row, col = pos_to_coords(pos, self.Ncol)
        return int(row), int(col)

    def coords_to_pos(self, coords):
        row, col = coords
        return int(coords_to_pos(row, col, self.Ncol))

    def set_fruit(self):
        """
        Spawn a fruit on a free cell.
        """
        free_positions = self.free_positions
        if free_positions.size == 0:
            self.status = 1
            return
        self.fruit_position = int(np.random.choice(free_positions))

    def get_grid(self):
        grid = self._grid
        grid[:, :] = self.void_color
        grid[self._wall_mask] = self.forbidden_color

        rows, cols = pos_to_coords(self.snake_active_positions, self.Ncol)
        grid[rows, cols] = self.snake_color
        grid[rows[0], cols[0]] = self.snake_head_color

        fruit_row, fruit_col = pos_to_coords(self.fruit_position, self.Ncol)
        grid[fruit_row, fruit_col] = self.fruit_color
        return grid

    grid = property(get_grid)

    def get_current_direction(self):
        """
        Return the current direction of motion.
        """
        head = self.head_position
        neck = int(self.snake_positions[1])
        if neck == head - 1:
            return DIR_RIGHT
        if neck == head + 1:
            return DIR_LEFT
        if neck == head + self.Ncol:
            return DIR_UP
        if neck == head - self.Ncol:
            return DIR_DOWN
        return -1

    def get_snake_direction_map(self):
        return DIRECTION_NAMES[self.get_current_direction()]

    def get_relative_turn_directions(self):
        current = self.get_current_direction()
        return np.array([(current + turn) % 4 for turn in TURN_IDS], dtype=np.int8)

    def get_neighbors_pos(self):
        neighbors = get_neighbors(self.head_position, self.Nrow, self.Ncol)
        return neighbors[self.get_relative_turn_directions()]

    def get_free_pos_matrix(self):
        return self._walkable_mask(self.snake_active_positions, free_tail=False)

    def _walkable_mask(self, snake_positions, free_tail=False):
        """
        Cells that can be traversed by future moves.
        The head cell is kept walkable and the tail can optionally be freed.
        """
        mask = ~self._wall_mask.copy()
        body = np.asarray(snake_positions[1:], dtype=np.int32)
        if free_tail and body.size != 0:
            body = body[:-1]
        if body.size != 0:
            rows, cols = pos_to_coords(body, self.Ncol)
            mask[rows, cols] = False
        head_row, head_col = pos_to_coords(int(snake_positions[0]), self.Ncol)
        mask[head_row, head_col] = True
        return mask

    def _path_length(self, walkable_mask, start_pos, target_pos):
        """
        Shortest path length on the walkable mask using 4-neighborhood BFS.
        Returns np.inf when target is unreachable.
        """
        if start_pos == target_pos:
            return 0.0

        start_row, start_col = pos_to_coords(start_pos, self.Ncol)
        target_row, target_col = pos_to_coords(target_pos, self.Ncol)
        if not walkable_mask[start_row, start_col]:
            return np.inf
        if not walkable_mask[target_row, target_col]:
            return np.inf

        visited = self._bfs_visited
        visited[:] = False
        visited[start_row, start_col] = True
        queue = deque([(int(start_row), int(start_col), 0)])

        while queue:
            row, col, dist = queue.popleft()
            for drow, dcol in DIRECTION_VECTORS.values():
                nrow = row + drow
                ncol = col + dcol
                if not (0 <= nrow < self.Nrow and 0 <= ncol < self.Ncol):
                    continue
                if visited[nrow, ncol] or not walkable_mask[nrow, ncol]:
                    continue
                if nrow == target_row and ncol == target_col:
                    return float(dist + 1)
                visited[nrow, ncol] = True
                queue.append((nrow, ncol, dist + 1))
        return np.inf

    def _component_size(self, walkable_mask, start_pos):
        start_row, start_col = pos_to_coords(start_pos, self.Ncol)
        if not walkable_mask[start_row, start_col]:
            return 0

        visited = self._bfs_visited
        visited[:] = False
        visited[start_row, start_col] = True
        queue = deque([(int(start_row), int(start_col))])
        count = 0

        while queue:
            row, col = queue.popleft()
            count += 1
            for drow, dcol in DIRECTION_VECTORS.values():
                nrow = row + drow
                ncol = col + dcol
                if not (0 <= nrow < self.Nrow and 0 <= ncol < self.Ncol):
                    continue
                if visited[nrow, ncol] or not walkable_mask[nrow, ncol]:
                    continue
                visited[nrow, ncol] = True
                queue.append((nrow, ncol))
        return count

    def _fruit_distance(self, pos):
        row, col = pos_to_coords(pos, self.Ncol)
        fruit_row, fruit_col = pos_to_coords(self.fruit_position, self.Ncol)
        return abs(int(row) - int(fruit_row)) + abs(int(col) - int(fruit_col))

    def _count_walkable_neighbors(self, walkable_mask, pos):
        neighbors = get_neighbors(int(pos), self.Nrow, self.Ncol)
        count = 0
        for neighbor in neighbors:
            if neighbor < 0:
                continue
            row, col = pos_to_coords(neighbor, self.Ncol)
            if walkable_mask[row, col]:
                count += 1
        return count

    def get_turn_neighbors(self):
        """
        Legacy 3-value sensor for [right, front, left].
        """
        blocked = np.zeros(self.Ncell, dtype=bool)
        blocked[self.forbidden_positions] = True
        blocked[self.snake_active_positions[1:]] = True
        out = np.zeros(3, dtype=np.float64)
        for i, pos in enumerate(self.get_neighbors_pos()):
            if pos == self.fruit_position:
                out[i] = 1.0
            elif pos < 0 or blocked[pos]:
                out[i] = -1.0
        return out

    def get_fruit_relative_vector(self, signed=False):
        """
        Fruit direction in the snake reference frame:
        - first component = forward/backward
        - second component = right/left
        """
        head_row, head_col = self.head_coords
        fruit_row, fruit_col = pos_to_coords(self.fruit_position, self.Ncol)
        delta = np.array(
            (float(fruit_row) - head_row, float(fruit_col) - head_col),
            dtype=np.float64,
        )
        norm = np.linalg.norm(delta)
        if norm == 0.0:
            out = np.zeros(2, dtype=np.float64)
        else:
            delta /= norm
            current = self.get_current_direction()
            if current == DIR_UP:
                out = np.array((-delta[0], delta[1]), dtype=np.float64)
            elif current == DIR_RIGHT:
                out = np.array((delta[1], delta[0]), dtype=np.float64)
            elif current == DIR_DOWN:
                out = np.array((delta[0], -delta[1]), dtype=np.float64)
            else:
                out = np.array((-delta[1], -delta[0]), dtype=np.float64)
        return np.sign(out) if signed else out

    def get_fruit_relative_directions(self):
        out = self.get_fruit_relative_vector(signed=True)
        return float(out[0]), float(out[1])

    def _ray_positions(self, direction):
        positions = []
        current = self.head_position
        while True:
            current = get_neighbors(current, self.Nrow, self.Ncol)[int(direction)]
            if current < 0:
                break
            positions.append(int(current))
            row, col = pos_to_coords(current, self.Ncol)
            if self._wall_mask[row, col]:
                break
        return positions

    def _distance_to_obstacle(self, ray_positions):
        blocked = np.zeros(self.Ncell, dtype=bool)
        blocked[self.forbidden_positions] = True
        blocked[self.snake_active_positions[1:]] = True
        for dist, pos in enumerate(ray_positions):
            if pos == self.fruit_position:
                return float(self.Ncell)
            if blocked[pos]:
                return float(dist)
        return float(len(ray_positions))

    def get_lidar(self):
        out = np.zeros(3, dtype=np.float64)
        for i, direction in enumerate(self.get_relative_turn_directions()):
            out[i] = self._distance_to_obstacle(self._ray_positions(direction))
        return out

    def get_enhanced_lidar(self):
        current = self.get_current_direction()
        diagonal_steps = np.array(
            [
                np.array(DIRECTION_VECTORS[(current + 2) % 4])
                + np.array(DIRECTION_VECTORS[(current + 1) % 4]),
                np.array(DIRECTION_VECTORS[(current - 1) % 4]),
                np.array(DIRECTION_VECTORS[current]),
                np.array(DIRECTION_VECTORS[(current + 1) % 4]),
                np.array(DIRECTION_VECTORS[(current + 2) % 4])
                + np.array(DIRECTION_VECTORS[(current - 1) % 4]),
            ]
        )

        snake_body = set(self.snake_active_positions[1:].tolist())
        out = np.zeros(5, dtype=np.float64)
        for i, step in enumerate(diagonal_steps):
            row, col = self.head_coords
            distance = 0.0
            while True:
                row += int(step[0])
                col += int(step[1])
                if not (0 <= row < self.Nrow and 0 <= col < self.Ncol):
                    break
                pos = int(coords_to_pos(row, col, self.Ncol))
                if self._wall_mask[row, col] or pos in snake_body:
                    break
                if pos == self.fruit_position:
                    distance = float(self.Ncell)
                    break
                distance += 1.0
            out[i] = distance
        return out

    def get_enhanched_lidar(self):
        return self.get_enhanced_lidar()

    def simulate_direction(self, direction):
        """
        Simulate an absolute direction without mutating the environment.
        """
        active = self.snake_active_positions
        head = int(active[0])
        new_head = int(get_neighbors(head, self.Nrow, self.Ncol)[int(direction)])

        result = {
            "direction": int(direction),
            "new_head": new_head,
            "status": 0,
            "ate_fruit": False,
            "snake_positions": active.copy(),
            "new_length": int(active.size),
        }

        if new_head < 0:
            result["status"] = -3
            return result

        if active.size > 1 and new_head == int(active[1]):
            result["status"] = -1
            return result

        eats_fruit = new_head == self.fruit_position
        if eats_fruit:
            new_snake = np.empty(active.size + 1, dtype=np.int32)
            new_snake[0] = new_head
            new_snake[1:] = active
        else:
            new_snake = np.empty(active.size, dtype=np.int32)
            new_snake[0] = new_head
            new_snake[1:] = active[:-1]

        new_row, new_col = pos_to_coords(new_head, self.Ncol)
        if self._wall_mask[new_row, new_col]:
            result["status"] = -2
        elif np.unique(new_snake).size != new_snake.size:
            result["status"] = -1

        result["snake_positions"] = new_snake
        result["new_length"] = int(new_snake.size)
        result["ate_fruit"] = eats_fruit
        return result

    def simulate_turn(self, turn):
        direction = (self.get_current_direction() + int(turn)) % 4
        result = self.simulate_direction(direction)
        result["turn"] = int(turn)
        return result

    def analyze_moves(self):
        """
        Analyze the three relative moves [right, front, left].
        """
        analyses = []
        old_distance = self._fruit_distance(self.head_position)
        for turn in TURN_IDS:
            simulation = self.simulate_turn(int(turn))
            if simulation["status"] != 0:
                analyses.append(
                    MoveAnalysis(
                        turn=int(turn),
                        direction=int(simulation["direction"]),
                        status=int(simulation["status"]),
                        safe=False,
                        eats_fruit=bool(simulation["ate_fruit"]),
                        new_head=int(simulation["new_head"]),
                        free_space_ratio=0.0,
                        tail_reachable=False,
                        fruit_path_length=np.inf,
                        tail_path_length=np.inf,
                        fruit_progress=-1.0,
                        branching_factor=0.0,
                    )
                )
                continue

            new_head = int(simulation["snake_positions"][0])
            new_tail = int(simulation["snake_positions"][-1])
            walkable_mask = self._walkable_mask(
                simulation["snake_positions"], free_tail=not simulation["ate_fruit"]
            )
            component_size = self._component_size(walkable_mask, new_head)
            free_space_ratio = component_size / max(1, int(walkable_mask.sum()))
            tail_path_length = self._path_length(walkable_mask, new_head, new_tail)
            tail_reachable = np.isfinite(tail_path_length)

            if simulation["ate_fruit"]:
                fruit_path_length = 0.0
                fruit_progress = 1.0
            else:
                fruit_path_length = self._path_length(
                    walkable_mask, new_head, self.fruit_position
                )
                new_distance = self._fruit_distance(new_head)
                fruit_progress = (
                    old_distance - new_distance
                ) / self.max_manhattan_distance

            branching_factor = (
                self._count_walkable_neighbors(walkable_mask, new_head) / 4.0
            )
            analyses.append(
                MoveAnalysis(
                    turn=int(turn),
                    direction=int(simulation["direction"]),
                    status=0,
                    safe=True,
                    eats_fruit=bool(simulation["ate_fruit"]),
                    new_head=new_head,
                    free_space_ratio=float(free_space_ratio),
                    tail_reachable=bool(tail_reachable),
                    fruit_path_length=float(fruit_path_length),
                    tail_path_length=float(tail_path_length),
                    fruit_progress=float(fruit_progress),
                    branching_factor=float(branching_factor),
                )
            )
        return analyses

    def _path_length_score(self, distance):
        if not np.isfinite(distance):
            return -1.0
        return 1.0 - min(distance, self.playable_cells) / self.playable_cells

    def _default_sensors(self):
        out = np.zeros(5, dtype=np.float64)
        out[:3] = self.get_turn_neighbors()
        out[3:] = self.get_fruit_relative_directions()
        return out

    def _compact_sensors(self):
        """
        Fixed-size sensor vector derived from full move analysis.
        """
        analyses = self.analyze_moves()
        out = np.zeros(21, dtype=np.float64)
        cursor = 0
        for analysis in analyses:
            out[cursor : cursor + 6] = np.array(
                [
                    1.0 if analysis.safe else -1.0,
                    1.0 if analysis.eats_fruit else 0.0,
                    analysis.free_space_ratio,
                    1.0 if analysis.tail_reachable else -1.0,
                    self._path_length_score(analysis.fruit_path_length),
                    self._path_length_score(analysis.tail_path_length),
                ],
                dtype=np.float64,
            )
            cursor += 6
        out[-3:-1] = self.get_fruit_relative_vector(signed=False)
        out[-1] = self.snake_length / self.playable_cells
        return out

    def _board_channels(self):
        """
        Return 4 channels:
        walls, body(without head), fruit, tail
        """
        walls = self._wall_mask.astype(np.float32)
        body = np.zeros((self.Nrow, self.Ncol), dtype=np.float32)
        fruit = np.zeros((self.Nrow, self.Ncol), dtype=np.float32)
        tail = np.zeros((self.Nrow, self.Ncol), dtype=np.float32)

        active = self.snake_active_positions
        if active.size > 1:
            rows, cols = pos_to_coords(active[1:], self.Ncol)
            body[rows, cols] = 1.0
        fruit_row, fruit_col = pos_to_coords(self.fruit_position, self.Ncol)
        fruit[fruit_row, fruit_col] = 1.0
        tail_row, tail_col = pos_to_coords(self.tail_position, self.Ncol)
        tail[tail_row, tail_col] = 1.0
        return np.stack((walls, body, fruit, tail), axis=0)

    def egocentric_channels(self, radius=None):
        """
        Return a head-centered observation aligned so the snake moves upward.

        If radius is None, the whole board is embedded in a centered canvas of
        shape (4, 2*Nrow-1, 2*Ncol-1).
        If radius is provided, a local crop of shape (4, 2*radius+1, 2*radius+1)
        is returned.
        """
        channels = self._board_channels()
        head_mask = np.zeros((self.Nrow, self.Ncol), dtype=np.float32)
        head_row, head_col = self.head_coords
        head_mask[head_row, head_col] = 1.0

        k = ROTATION_TO_UP[self.get_current_direction()]
        rotated_channels = np.rot90(channels, k=k, axes=(1, 2))
        rotated_head = np.rot90(head_mask, k=k)
        rotated_head_row, rotated_head_col = np.argwhere(rotated_head == 1.0)[0]

        centered = self._center_buffer
        centered[:] = 0.0
        target_row = self.Nrow - 1
        target_col = self.Ncol - 1
        row_offset = target_row - int(rotated_head_row)
        col_offset = target_col - int(rotated_head_col)
        row_slice = slice(row_offset, row_offset + rotated_channels.shape[1])
        col_slice = slice(col_offset, col_offset + rotated_channels.shape[2])
        centered[:, row_slice, col_slice] = rotated_channels

        if radius is None:
            return centered.copy()

        center_row = self.Nrow - 1
        center_col = self.Ncol - 1
        row_slice = slice(center_row - radius, center_row + radius + 1)
        col_slice = slice(center_col - radius, center_col + radius + 1)
        return centered[:, row_slice, col_slice].copy()

    def _egocentric_flat_sensors(self):
        return self.egocentric_channels(radius=None).ravel()

    def sensors(self, method="default", **kwargs):
        """
        Public observation API.

        Supported methods:
        - default: legacy 5-value sensor
        - compact / topology: fixed-size 21-value topology features
        - egocentric: flattened full head-centered grid

        Use egocentric_channels(radius=...) directly for tensor observations.
        """
        if method == "egocentric":
            radius = kwargs.get("radius")
            return self.egocentric_channels(radius=radius).ravel()
        try:
            return self._sensor_methods[method]()
        except KeyError as exc:
            available = ", ".join(sorted(self._sensor_methods))
            raise ValueError(
                f"Unknown sensor method '{method}'. Available methods: {available}, egocentric."
            ) from exc

    def get_label_sensors(self):
        """
        Compatibility helper kept for the notebook API.
        It now returns the best compact move according to free-space ratio.
        """
        analyses = self.analyze_moves()
        values = np.array([analysis.free_space_ratio for analysis in analyses])
        out = -np.ones(3, dtype=np.float64)
        if np.all(values <= 0.0):
            return out
        out[values == values.max()] = 1.0
        return out

    def check_defeat(self):
        active = self.snake_active_positions
        if np.unique(active).size != active.size:
            self.status = -1
        else:
            head_row, head_col = self.head_coords
            if self._wall_mask[head_row, head_col]:
                self.status = -2

    def play(self, direction):
        """
        Execute an absolute direction.
        """
        if self.status != 0:
            return self.status

        simulation = self.simulate_direction(direction)
        self.iteration += 1
        if simulation["status"] != 0:
            self.status = int(simulation["status"])
            return self.status

        self.snake_length = int(simulation["new_length"])
        self.snake_positions[: self.snake_length] = simulation["snake_positions"]

        if simulation["ate_fruit"]:
            self.score += 1
            self.set_fruit()

        self.check_defeat()
        return self.status

    def turn(self, turn):
        """
        Execute a relative turn:
        -1 = right, 0 = front, 1 = left
        """
        if self.status != 0:
            return

        if self.record_turns:
            self.recorded_turns.append(int(turn))
            self.recorded_sensors.append(
                self.sensors(method=self.recorded_sensors_method)
            )
            self.recorded_status.append(self.status)

        direction = (self.get_current_direction() + int(turn)) % 4
        self.play(direction)

    def get_snake_metrics(self):
        analyses = self.analyze_moves()
        print(f"Snake length: {self.snake_length}")
        print(f"Head position: {self.head_position}")
        print(f"Direction: {self.get_snake_direction_map()}")
        print(f"Default sensors: {self.sensors(method='default')}")
        print(f"Compact sensors: {self.sensors(method='compact')}")
        print("Move analyses:")
        for analysis in analyses:
            print(analysis)


class RandomTurnAgent:
    """
    Baseline agent returning random relative turns.
    """

    def __call__(self, snake):
        return int(np.random.choice(TURN_IDS))


class SafePathAgent:
    """
    Robust search-based agent used as a demonstration baseline.

    Strategy:
    1. Prefer legal moves that keep the tail reachable.
    2. Among them, prefer moves with a path to the fruit.
    3. Otherwise follow the tail or maximize free space.

    This is not optimal, but it is strong enough to avoid most self-wrapping
    failures on moderate grid sizes and is fully deterministic.
    """

    def __init__(self, cautious_length_ratio=0.35, roomy_threshold=0.55):
        self.cautious_length_ratio = cautious_length_ratio
        self.roomy_threshold = roomy_threshold

    def __call__(self, snake):
        analyses = snake.analyze_moves()
        legal = [analysis for analysis in analyses if analysis.safe]
        if not legal:
            return TURN_FRONT

        length_ratio = snake.snake_length / snake.playable_cells
        fruit_candidates = [
            analysis
            for analysis in legal
            if analysis.eats_fruit or np.isfinite(analysis.fruit_path_length)
        ]
        if fruit_candidates and length_ratio < self.cautious_length_ratio:
            best = min(
                fruit_candidates,
                key=lambda analysis: (
                    not analysis.eats_fruit,
                    analysis.fruit_path_length,
                    -analysis.free_space_ratio,
                    -analysis.branching_factor,
                ),
            )
            return best.turn

        safe_tail = [analysis for analysis in legal if analysis.tail_reachable]
        if safe_tail:
            fruit_safe = [
                analysis
                for analysis in safe_tail
                if analysis.eats_fruit or np.isfinite(analysis.fruit_path_length)
            ]
            if fruit_safe:
                best = min(
                    fruit_safe,
                    key=lambda analysis: (
                        not analysis.eats_fruit,
                        analysis.fruit_path_length,
                        -analysis.free_space_ratio,
                        -analysis.branching_factor,
                    ),
                )
                return best.turn

            roomy_fruit = [
                analysis
                for analysis in legal
                if (
                    analysis.eats_fruit
                    or np.isfinite(analysis.fruit_path_length)
                    and analysis.free_space_ratio >= self.roomy_threshold
                )
            ]
            if roomy_fruit:
                best = min(
                    roomy_fruit,
                    key=lambda analysis: (
                        not analysis.eats_fruit,
                        analysis.fruit_path_length,
                        -analysis.free_space_ratio,
                        -analysis.branching_factor,
                    ),
                )
                return best.turn

            tail_candidates = [
                analysis
                for analysis in safe_tail
                if np.isfinite(analysis.tail_path_length)
            ]
            if tail_candidates:
                best = min(
                    tail_candidates,
                    key=lambda analysis: (
                        analysis.tail_path_length,
                        -analysis.free_space_ratio,
                        -analysis.branching_factor,
                    ),
                )
                return best.turn

            best = max(
                safe_tail,
                key=lambda analysis: (
                    analysis.free_space_ratio,
                    analysis.branching_factor,
                    analysis.fruit_progress,
                ),
            )
            return best.turn

        best = max(
            legal,
            key=lambda analysis: (
                analysis.free_space_ratio,
                analysis.branching_factor,
                analysis.fruit_progress,
            ),
        )
        return best.turn


def run_episode(snake, agent, max_turns=None, fix_seed=None):
    """
    Run one episode and return summary statistics.
    """
    snake.reset(fix_seed=fix_seed)
    if hasattr(agent, "reset"):
        agent.reset()
    if max_turns is None:
        max_turns = 4 * snake.Ncell

    turns = 0
    while snake.status == 0 and turns < max_turns:
        turn = agent(snake)
        snake.turn(turn)
        turns += 1

    return {
        "score": int(snake.score),
        "turns": int(turns),
        "status": int(snake.status),
        "length": int(snake.snake_length),
        "won": bool(snake.status == 1),
    }


def benchmark_agent(agent, Nrow=12, Ncol=12, episodes=20, max_turns=None, seed=0):
    """
    Benchmark an agent on repeated episodes.
    """
    np.random.seed(seed)
    snake = FastSnake(Nrow=Nrow, Ncol=Ncol)
    stats = [run_episode(snake, agent, max_turns=max_turns) for _ in range(episodes)]
    scores = np.array([item["score"] for item in stats], dtype=np.float64)
    turns = np.array([item["turns"] for item in stats], dtype=np.float64)
    wins = np.array([item["won"] for item in stats], dtype=np.float64)
    return {
        "episodes": int(episodes),
        "mean_score": float(scores.mean()),
        "max_score": int(scores.max(initial=0)),
        "mean_turns": float(turns.mean()),
        "win_rate": float(wins.mean()),
        "raw": stats,
    }


def show_gui(snake, ax, return_metrics=False):
    left_widget = widgets.Button(
        description="snake.turn(+1)",
        button_style="success",
        tooltip="Turn left",
        icon="fa-arrow-left",
    )
    right_widget = widgets.Button(
        description="snake.turn(-1)",
        button_style="success",
        tooltip="Turn right",
        icon="fa-arrow-right",
    )
    up_widget = widgets.Button(
        description="snake.turn(0)",
        button_style="success",
        tooltip="Go straight",
        icon="fa-arrow-up",
    )
    reset_widget = widgets.Button(
        description="Reset",
        button_style="danger",
        tooltip="Reset",
        icon="fa-power-off",
    )

    def set_turn(turn):
        snake.turn(turn)
        update_fig()

    def reset_game():
        snake.reset()
        update_fig()

    left_widget.on_click(lambda arg: set_turn(1.0))
    right_widget.on_click(lambda arg: set_turn(-1.0))
    up_widget.on_click(lambda arg: set_turn(0.0))
    reset_widget.on_click(lambda arg: reset_game())

    def update_fig():
        im.set_array(snake.grid)
        if snake.status == 0:
            message = "PLAY"
        elif snake.status == -1:
            message = "YOU DIED (YOURSELF)"
        elif snake.status == -2:
            message = "YOU DIED (WALL)"
        elif snake.status == -3:
            message = "YOU DIED (OUT OF BOUNDS)"
        else:
            message = "WIN"

        if snake.display_sensor_method is None:
            sensors = ""
        else:
            sensors = str(snake.sensors(method=snake.display_sensor_method))
        title.set_text(f"Score = {snake.score}, {message} {sensors}")
        plt.draw()
        return (im,)

    ax.axis("off")
    title = ax.set_title(f"Score = {snake.score}, PLAY")
    im = ax.imshow(snake.grid, interpolation="nearest", animated=True)
    update_fig()
    box = widgets.Box([left_widget, right_widget, up_widget, reset_widget])

    entries = {"Head": "gray", "Body": "black", "Wall": "red", "Fruit": "green"}
    handles = [
        ax.plot([], [], marker="s", color=color, ls="none")[0]
        for color in entries.values()
    ]
    ax.legend(handles, list(entries.keys()), loc=(1.1, 0), frameon=False)
    return box


class NeuralAgent:
    """
    Small dense neural network helper kept for educational notebooks.
    """

    def __init__(self, weights, structure, neural_functions, use_bias=True):
        matrices = []
        start = 0
        for i in range(len(structure) - 1):
            nin = structure[i]
            nout = structure[i + 1]
            Nw = (nin + 1) * nout
            w = weights[start : start + Nw]
            start += Nw
            A = w[:-nout].reshape(nout, nin)
            B = w[-nout:]
            matrices.append((A, B))
        self.structure = structure
        self.matrices = matrices
        self.neural_functions = neural_functions
        self.weights = weights
        self.use_bias = use_bias

    def get_caller(self):
        matrices = self.matrices
        neural_functions = self.neural_functions
        use_bias = self.use_bias

        def inference(x):
            x = np.asarray(x, dtype=np.float64)
            for stage, (A, B) in enumerate(matrices):
                x = A @ x
                if use_bias:
                    x = x + B
                x = neural_functions[stage](x)
            return x

        return inference


class RecurrentNeuralAgent:
    """
    Minimal recurrent agent for genetic optimization.

    The network receives the current observation concatenated with an explicit
    memory vector `m_t` and outputs:

    - `action_scores_t`
    - `m_{t+1}`

    This is intentionally simple:

    - no backpropagation-specific machinery
    - no gates
    - one explicit memory state that can be evolved genetically

    It is a good teaching compromise between a feed-forward MLP and a full RNN.
    """

    def __init__(
        self,
        weights,
        observation_size,
        memory_size,
        hidden_sizes=(8,),
        action_size=3,
        hidden_activation=np.tanh,
        output_activation=lambda x: x,
        memory_activation=np.tanh,
        use_bias=True,
    ):
        self.observation_size = int(observation_size)
        self.memory_size = int(memory_size)
        self.action_size = int(action_size)
        self.hidden_sizes = tuple(int(size) for size in hidden_sizes)
        self.hidden_activation = hidden_activation
        self.output_activation = output_activation
        self.memory_activation = memory_activation
        self.use_bias = use_bias
        self.weights = np.asarray(weights, dtype=np.float64)

        self.structure = (
            self.observation_size + self.memory_size,
            *self.hidden_sizes,
            self.action_size + self.memory_size,
        )
        self.matrices = self._unpack_weights(self.weights, self.structure)

    @staticmethod
    def count_weights(observation_size, memory_size, hidden_sizes=(8,), action_size=3):
        """
        Return the number of scalar parameters needed by the recurrent MLP.
        """
        structure = (
            int(observation_size) + int(memory_size),
            *(int(size) for size in hidden_sizes),
            int(action_size) + int(memory_size),
        )
        count = 0
        for i in range(len(structure) - 1):
            count += (structure[i] + 1) * structure[i + 1]
        return count

    def _unpack_weights(self, weights, structure):
        matrices = []
        start = 0
        for i in range(len(structure) - 1):
            nin = structure[i]
            nout = structure[i + 1]
            nw = (nin + 1) * nout
            w = weights[start : start + nw]
            start += nw
            A = w[:-nout].reshape(nout, nin)
            B = w[-nout:]
            matrices.append((A, B))
        if start != weights.size:
            raise ValueError(
                f"Weight vector size mismatch: expected {start}, got {weights.size}."
            )
        return matrices

    def initial_memory(self):
        """
        Return a zero-initialized recurrent memory state.
        """
        return np.zeros(self.memory_size, dtype=np.float64)

    def forward(self, observation, memory=None):
        """
        Run one recurrent step.

        Parameters
        ----------
        observation : array-like
            Observation vector at time t.
        memory : array-like or None
            Memory vector m_t. When None, a zero memory is used.

        Returns
        -------
        action_scores : ndarray
            Action logits/scores for the current time step.
        new_memory : ndarray
            Memory vector m_{t+1}.
        """
        observation = np.asarray(observation, dtype=np.float64)
        if observation.shape != (self.observation_size,):
            raise ValueError(
                f"Observation shape mismatch: expected {(self.observation_size,)}, got {observation.shape}."
            )

        if memory is None:
            memory = self.initial_memory()
        else:
            memory = np.asarray(memory, dtype=np.float64)
            if memory.shape != (self.memory_size,):
                raise ValueError(
                    f"Memory shape mismatch: expected {(self.memory_size,)}, got {memory.shape}."
                )

        x = np.concatenate((observation, memory))
        for stage, (A, B) in enumerate(self.matrices):
            x = A @ x
            if self.use_bias:
                x = x + B
            if stage < len(self.matrices) - 1:
                x = self.hidden_activation(x)
            else:
                x = self.output_activation(x)

        action_scores = x[: self.action_size]
        new_memory = self.memory_activation(x[self.action_size :])
        return action_scores, new_memory

    def get_caller(self):
        """
        Return a stateless recurrent caller:
        `(observation, memory) -> (action_scores, new_memory)`.
        """

        def recurrent_inference(observation, memory=None):
            return self.forward(observation, memory=memory)

        return recurrent_inference

    def get_stateful_caller(self, initial_memory=None):
        """
        Return a stateful caller suitable for episode rollouts.

        The returned callable exposes:
        - `reset(memory=None)`
        - `get_memory()`
        """
        memory = (
            self.initial_memory()
            if initial_memory is None
            else np.asarray(initial_memory, dtype=np.float64).copy()
        )

        if memory.shape != (self.memory_size,):
            raise ValueError(
                f"Initial memory shape mismatch: expected {(self.memory_size,)}, got {memory.shape}."
            )

        def inference(observation):
            nonlocal memory
            action_scores, memory = self.forward(observation, memory=memory)
            return action_scores

        def reset(memory_value=None):
            nonlocal memory
            if memory_value is None:
                memory = self.initial_memory()
            else:
                memory = np.asarray(memory_value, dtype=np.float64).copy()
                if memory.shape != (self.memory_size,):
                    raise ValueError(
                        f"Reset memory shape mismatch: expected {(self.memory_size,)}, got {memory.shape}."
                    )

        def get_memory():
            return memory.copy()

        inference.reset = reset
        inference.get_memory = get_memory
        return inference


class RecurrentPolicyAgent:
    """
    Small adapter between `FastSnake` observations and `RecurrentNeuralAgent`.

    This is the most convenient interface for a genetic exercise:

    1. choose an observation method (`compact`, `default`, `egocentric`, ...)
    2. evolve the recurrent network weights
    3. evaluate the policy directly through `run_episode`
    """

    def __init__(
        self,
        network,
        sensor_method="compact",
        sensor_kwargs=None,
        turn_ids=TURN_IDS,
    ):
        self.network = network
        self.sensor_method = sensor_method
        self.sensor_kwargs = {} if sensor_kwargs is None else dict(sensor_kwargs)
        self.turn_ids = np.asarray(turn_ids, dtype=np.int8)
        self.memory = self.network.initial_memory()

    def reset(self):
        self.memory = self.network.initial_memory()

    def get_observation(self, snake):
        observation = snake.sensors(method=self.sensor_method, **self.sensor_kwargs)
        return np.asarray(observation, dtype=np.float64)

    def __call__(self, snake):
        observation = self.get_observation(snake)
        action_scores, self.memory = self.network.forward(
            observation, memory=self.memory
        )
        action_index = int(np.argmax(action_scores))
        return int(self.turn_ids[action_index])
