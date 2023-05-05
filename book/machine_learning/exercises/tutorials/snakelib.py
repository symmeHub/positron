import numpy as np


class FastSnake:
    """
    A fast numpy based Snake
    """

    def __init__(
        self,
        Nrow,
        Ncol,
        snake_color=(0, 0, 0),
        snake_head_color=(128, 128, 128),
        forbidden_color=(255, 0, 0),
        fruit_color=(0, 255, 0),
        void_color=(255, 255, 255),
    ):
        self.Nrow = Nrow
        self.Ncol = Ncol
        Ncell = Nrow * Ncol
        self.Ncell = Nrow * Ncol
        self.all_positions = all_positions = np.arange(Ncell)
        self.grid_values = grid_values = all_positions.reshape(Nrow, Ncol)
        forbidden_positions = np.unique(
            np.concatenate(
                [grid_values[0], grid_values[-1], grid_values[:, 0], grid_values[:, -1]]
            )
        )
        self.forbidden_positions = forbidden_positions
        self._grid = np.ones((Nrow, Ncol, 3), dtype=np.uint8) * 255
        authorized_positions = np.setdiff1d(all_positions, forbidden_positions)
        self.authorized_positions = authorized_positions
        self.snake_color = snake_color
        self.snake_head_color = snake_head_color
        self.forbidden_color = forbidden_color
        self.fruit_color = fruit_color
        self.void_color = void_color
        self.reset()
        # SENSORS
        sr, sc = np.meshgrid(np.arange(-1, 2), np.arange(-1, 2))
        self.sensor_offsets = np.array([sr.flatten(), sc.flatten()]).T.copy()

    def reset(self):
        all_positions = self.all_positions
        Ncell = self.Ncell
        grid_values = self.grid_values
        snake_positions = np.zeros_like(all_positions)
        snake_active = np.zeros(Ncell, dtype=np.bool)
        snake_active[:2] = True
        snake_positions[:2] = grid_values[1:3, 1]
        self.snake_positions = snake_positions
        self.snake_active = snake_active
        self.set_fruit()
        self.status = 0
        self.score = 0

    def get_snake_active_positions(self):
        return self.snake_positions[self.snake_active]

    snake_active_positions = property(get_snake_active_positions)

    def get_free_positions(self):
        all_positions = self.all_positions
        forbidden_positions = self.forbidden_positions
        snake_positions = self.snake_active_positions
        free_positions = np.setdiff1d(
            all_positions, np.union1d(forbidden_positions, snake_positions)
        )
        return free_positions

    free_positions = property(get_free_positions)

    def set_fruit(self):
        fp = self.free_positions
        if len(fp) != 0:
            self.fruit_position = np.random.choice(fp)
        else:
            self.status = 1

    def get_grid(self):
        Nrow = self.Nrow
        Ncol = self.Ncol
        grid = self._grid
        grid[:, :] = self.void_color
        # SNAKE
        snake_color = self.snake_color
        spos = self.snake_positions[self.snake_active]
        # srows = spos // Ncol
        # scols = spos % Ncol
        srows, scols = pos_to_coords(spos, Ncol)
        grid[srows, scols] = snake_color
        grid[srows[0], scols[0]] = self.snake_head_color

        # FORBIDDEN
        forbidden_positions = self.forbidden_positions
        forbidden_color = self.forbidden_color
        # frows = forbidden_positions // Ncol
        # fcols = forbidden_positions % Ncol
        frows, fcols = pos_to_coords(forbidden_positions, Ncol)
        grid[forbidden_positions // Ncol, forbidden_positions % Ncol] = forbidden_color

        # FRUIT
        fruit_position = self.fruit_position
        # frrows = fruit_position // Ncol
        # frcols = fruit_position % Ncol
        frrows, frcols = pos_to_coords(fruit_position, Ncol)
        grid[frrows, frcols] = self.fruit_color

        return grid

    grid = property(get_grid)

    def check_defeat(self):
        forbidden_positions = self.forbidden_positions
        snake_positions = self.snake_active_positions
        if np.unique(snake_positions).size != snake_positions.size:
            self.status = -1
        if np.intersect1d(forbidden_positions, snake_positions).size != 0:
            self.status = -2

    def play(self, direction):
        if self.status != 0:
            return self.status
        else:
            snake_positions = self.snake_positions
            fruit_position = self.fruit_position
            head = snake_positions[0]
            neigh = get_neighbors(head, self.Nrow, self.Ncol)
            new_head = neigh[direction]
            if new_head == snake_positions[1]:
                self.status = -1
            elif new_head < 0:
                self.status = -3
            else:
                snake_positions[1:] = snake_positions[:-1]
                snake_positions[0] = new_head
                if new_head == fruit_position:
                    self.set_fruit()
                    sap = self.snake_active
                    sap[:] = np.roll(sap, 1)
                    sap[0] = True
                    self.score += 1
            self.check_defeat()
            return self.status

    # def sensors(self):
    #     out = np.zeros(10, dtype=np.float64) + 0.5
    #     # MOORE NEIGHBOROOD
    #     snake_positions = self.snake_active_positions
    #     snake_head_position = snake_positions[0]
    #     snake_tail_positions = snake_positions[1:]
    #     fruit_position = self.fruit_position
    #     forbidden_positions = self.forbidden_positions
    #     moore = get_Moore_neighbors(snake_head_position, self.Ncol)
    #     tail_and_lava = np.union1d(snake_tail_positions, forbidden_positions)
    #     out[:8][np.isin(moore, tail_and_lava)] = 0.0
    #     out[:8][moore == fruit_position] = 1.0
    #     # FRUIT DIRECTION
    #     head_coords = pos_to_coords(snake_head_position, self.Ncol)
    #     fruit_coords = pos_to_coords(fruit_position, self.Ncol)
    #     dcol, drow = fruit_coords[1] - head_coords[1], fruit_coords[0] - head_coords[0]
    #     out[8] = dcol
    #     out[9] = drow
    #     return out
    def sensors(self):
        out = np.zeros(7, dtype=np.float64)
        # MOORE NEIGHBOROOD
        snake_positions = self.snake_active_positions
        snake_head_position = snake_positions[0]
        snake_tail_positions = snake_positions[1:]
        fruit_position = self.fruit_position
        forbidden_positions = self.forbidden_positions
        neigh = get_neighbors(snake_head_position, self.Nrow, self.Ncol)
        tail_and_lava = np.union1d(snake_tail_positions, forbidden_positions)
        out[:4][np.isin(neigh, tail_and_lava)] = -1.0
        out[:4][neigh == fruit_position] = 1.0
        # FRUIT DIRECTION
        head_coords = np.array(pos_to_coords(snake_head_position, self.Ncol))
        fruit_coords = np.array(pos_to_coords(fruit_position, self.Ncol))
        dcol, drow = fruit_coords[1] - head_coords[1], fruit_coords[0] - head_coords[0]
        # if dcol != 0.0:
        #     decol = np.sign(dcol)
        # if drow != 0.0:
        #     drow = np.sign(drow)
        # out[4] = dcol
        # out[5] = drow
        # NECK DIRECTION
        head_coords = np.array(pos_to_coords(snake_head_position, self.Ncol))
        neck_coords = np.array(pos_to_coords(snake_tail_positions[0], self.Ncol))
        neckcol, neckrow = (
            neck_coords[1] - head_coords[1],
            neck_coords[0] - head_coords[0],
        )

        if neckcol == 1:
            ndirection = 0
        elif neckcol == -1:
            ndirection = 2
        elif neckrow == 1.0:
            ndirection = 1
        elif neckrow == -1.0:
            ndirection = 3
        else:
            direction = -1.0
        out[4] = ndirection
        out[5:] = np.sign([dcol, -drow])
        return out


def get_neighbors(pos, Nrow, Ncol):
    """
    Returns the neighbors of a given cell with the following order: top, bottom, left, right. If neighbor does not exist, value is -1.
    """
    out = np.ones(4, dtype=np.int32) * -1
    # TOP:
    dv = pos // Ncol
    if dv != 0:
        out[1] = pos - Ncol
    # BOTTOM
    if dv < Nrow - 1:
        out[3] = pos + Ncol
    dh = pos % Ncol
    # LEFT
    if dh != 0:
        out[2] = pos - 1
    # RIGHT
    if dh < Ncol - 1:
        out[0] = pos + 1
    return out


def pos_to_coords(pos, Ncol):
    """
    Returns the coordinates of a given position
    """
    r = pos // Ncol
    c = pos % Ncol
    return r, c


def get_Moore_neighbors(pos, Ncol):
    """
    Returns the Moore neighbors of the cell position.
    """
    out = np.zeros(8, dtype=np.uint32)
    out[0] = pos + 1
    out[1] = pos - Ncol + 1
    out[2] = pos - Ncol
    out[3] = pos - Ncol - 1
    out[4] = pos - 1
    out[5] = pos + Ncol - 1
    out[6] = pos + Ncol
    out[7] = pos + Ncol + 1
    return out
