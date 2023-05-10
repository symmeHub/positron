import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
from matplotlib import animation


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
            new_head = neigh[int(direction)]
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

    def turn(self, turn):
        """
        turn = 0: go forward
        turn == 1: go left
        turn == -1: go right
        """
        current_direction = self.get_current_direction()
        abs_direction = (current_direction + turn) % 4
        self.play(abs_direction)

    def get_current_direction(self):
        snake_positions = self.snake_active_positions
        head_position = snake_positions[0]
        neck_position = snake_positions[1]
        Ncol = self.Ncol
        direction = -1
        if neck_position == head_position - 1:
            direction = 0
        elif neck_position == head_position + 1:
            direction = 2
        elif neck_position == head_position + Ncol:
            direction = 1
        elif neck_position == head_position - Ncol:
            direction = 3
        else:
            direction = -1
        return direction

    def get_fruit_relative_directions(self):
        snake_positions = self.snake_active_positions
        snake_head_position = snake_positions[0]
        fruit_position = self.fruit_position
        head_coords = np.array(pos_to_coords(snake_head_position, self.Ncol))
        fruit_coords = np.array(pos_to_coords(fruit_position, self.Ncol))
        dcol, drow = fruit_coords[1] - head_coords[1], fruit_coords[0] - head_coords[0]
        d = np.sqrt(dcol**2 + drow**2)
        cdir = self.get_current_direction()
        if cdir == 0:
            asin = -drow / d
            acos = dcol / d

        elif cdir == 2:
            asin = drow / d
            acos = -dcol / d
        elif cdir == 1:
            asin = -dcol / d
            acos = -drow / d

        elif cdir == 3:
            asin = dcol / d
            acos = drow / d
        return acos, asin

    def get_turn_neighbors(self):
        Ncol = self.Ncol
        headpos = self.snake_active_positions[0]
        forbidden_positions = self.forbidden_positions
        snake_tail_positions = self.snake_active_positions[1:]
        tail_and_lava = np.union1d(snake_tail_positions, forbidden_positions)
        fruit_position = self.fruit_position
        fdir = self.get_current_direction()
        ldir = (fdir + 1) % 4
        rdir = (fdir - 1) % 4
        if fdir == 0:
            frontpos = headpos + 1
            leftpos = headpos - Ncol
            rightpos = headpos + Ncol
        if fdir == 1:
            frontpos = headpos - Ncol
            leftpos = headpos - 1
            rightpos = headpos + 1
        if fdir == 2:
            frontpos = headpos - 1
            leftpos = headpos + Ncol
            rightpos = headpos - Ncol
        if fdir == 3:
            frontpos = headpos + Ncol
            leftpos = headpos + 1
            rightpos = headpos - 1
        positions = np.array([leftpos, frontpos, rightpos])
        out = np.zeros(3)
        for i in range(3):
            pos = positions[i]
            if pos == fruit_position:
                out[i] = 1.0
            elif pos in tail_and_lava:
                out[i] = -1
        return out

    def get_lidar(self):
        """
        # TODO
        """
        return

    def sensors(self, method="default"):
        if method == "default":
            out = np.zeros(5, dtype=np.float64)
            out[:3] = self.get_turn_neighbors()
            out[3:] = self.get_fruit_relative_directions()
            return out
        # if method == "advanced":
        #     out = np.zeros(9, dtype=np.float64)
        #     out[:3] = self.get_turn_neighbors()
        #     out[3:] = self.get_fruit_relative_directions()
        #     return out


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


def get_rank2_Moore_neighbors(pos, Ncol, Nrow):
    """
    Returns the Moore neighbors of the cell position.
    """
    out = np.zeros(24, dtype=np.uint32)
    out[0] = pos + 1
    out[1] = pos - Ncol + 1
    out[2] = pos - Ncol
    out[3] = pos - Ncol - 1
    out[4] = pos - 1
    out[5] = pos + Ncol - 1
    out[6] = pos + Ncol
    out[7] = pos + Ncol + 1
    return out


def show_gui(snake, ax):
    # RELATIVE TURNS

    left_widget = widgets.Button(
        description="snake.turn(+1)",
        disabled=False,
        button_style="success",
        tooltip="Want to go left ?",
        icon="fa-arrow-left",
    )

    right_widget = widgets.Button(
        description="snake.turn(-1)",
        disabled=False,
        button_style="success",
        tooltip="Want to go right ?",
        icon="fa-arrow-right",
    )

    up_widget = widgets.Button(
        description="snake.turn(0)",
        disabled=False,
        button_style="success",
        tooltip="Want to go up ?",
        icon="fa-arrow-up",
    )

    reset_widget = widgets.Button(
        description="Reset",
        disabled=False,
        button_style="danger",
        tooltip="Want to reset ?",
        icon="fa-power-off",
    )

    # direction = 0

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
        status = snake.status
        if status == 0:
            mess = "PLAY"
        elif status == -1:
            mess = "YOU DIED (YOURSELF)"
        elif status == -2:
            mess = "YOU DIED (LAVA)"
        title.set_text(f"Score = {snake.score}, {mess}")
        plt.draw()
        return (im,)

    ax.axis("off")
    title = ax.set_title(f"Score = {snake.score}, PLAY ")
    im = ax.imshow(snake.grid, interpolation="nearest", animated=True)
    box = widgets.Box([left_widget, right_widget, up_widget, reset_widget])
    return box


class NeuralAgent:
    """
    A NEURAL NETWORK AGENT
    """

    def __init__(self, weights, structure, neural_functions):
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
            matrices.append([A, B])
        self.structure = structure
        self.matrices = matrices
        self.neural_functions = neural_functions
        self.weights = weights

    def get_caller(self):
        matrices = self.matrices
        neural_functions = self.neural_functions

        def inference(x):
            for stage in range(len(matrices)):
                A, B = matrices[stage]
                x = A @ x + B
                x = neural_functions[stage](x)
            return x

        return inference
