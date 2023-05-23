import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt
from matplotlib import animation


class FastSnake:
    """
    A fast numpy based Snake game.

    Parameters
    ----------
    Nrow : int
        The number of rows in the game grid.
    Ncol : int
        The number of columns in the game grid.
    snake_color : tuple of int, optional
        The RGB color tuple for the snake's body. Default is (0, 0, 0).
    snake_head_color : tuple of int, optional
        The RGB color tuple for the snake's head. Default is (128, 128, 128).
    forbidden_color : tuple of int, optional
        The RGB color tuple for the forbidden area. Default is (255, 0, 0).
    fruit_color : tuple of int, optional
        The RGB color tuple for the fruit. Default is (0, 255, 0).
    void_color : tuple of int, optional
        The RGB color tuple for the empty space in the game grid. Default is (255, 255, 255).

    Attributes
    ----------
    Nrow : int
        The number of rows in the game grid.
    Ncol : int
        The number of columns in the game grid.
    Ncell : int
        The total number of cells in the game grid.
    all_positions : numpy.ndarray
        An array containing all possible cell positions in the game grid.
    grid_values : numpy.ndarray
        A 2D array representing the game grid.
    forbidden_positions : numpy.ndarray
        An array containing the positions of the forbidden areas in the game grid.
    _grid : numpy.ndarray
        A 3D array representing the game grid with RGB colors.
    authorized_positions : numpy.ndarray
        An array containing the positions of the authorized areas in the game grid.
    snake_color : tuple of int
        The RGB color tuple for the snake's body.
    snake_head_color : tuple of int
        The RGB color tuple for the snake's head.
    forbidden_color : tuple of int
        The RGB color tuple for the forbidden area.
    fruit_color : tuple of int
        The RGB color tuple for the fruit.
    void_color : tuple of int
        The RGB color tuple for the empty space in the game grid.

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

    def reset(self, fix_seed=None):
        """
        Resets the game grid to its initial state by initializing snake and fruit positions, and resetting the score and status.
        Optional parameter fix_seed (int) can be used to fix the random seed for the fruit position.
        Returns
        -------
        None
        """
        # Get the attributes of the game grid
        all_positions = self.all_positions
        Ncell = self.Ncell
        grid_values = self.grid_values

        # Initialize the snake's positions and activation status
        snake_positions = np.zeros_like(all_positions)
        snake_active = np.zeros(Ncell, dtype=np.bool)
        snake_active[:2] = True  # Set the first two positions as active
        snake_positions[:2] = grid_values[1:3, 1]  # Set the initial snake position
        self.snake_positions = snake_positions
        self.snake_active = snake_active

        # Set the initial fruit position and reset the score and status
        if fix_seed:
            np.random.seed(fix_seed)

        self.set_fruit()
        self.status = 0
        self.score = 0

    def get_snake_active_positions(self):
        """
        Returns the positions of the active (alive) snake.

        Returns
        -------
        ndarray
            A 1D numpy array of the active snake positions.
        """
        return self.snake_positions[self.snake_active]

    # Define a property for the active snake positions
    snake_active_positions = property(get_snake_active_positions)

    def get_free_positions(self):
        """
        Returns the positions on the game grid that are not forbidden or occupied by the active snake.

        Returns
        -------
        ndarray
            A 1D numpy array of the free positions on the game grid.
        """
        all_positions = self.all_positions
        forbidden_positions = self.forbidden_positions
        snake_positions = self.snake_active_positions
        free_positions = np.setdiff1d(
            all_positions, np.union1d(forbidden_positions, snake_positions)
        )
        return free_positions

    # Define a property for the free positions on the game grid
    free_positions = property(get_free_positions)

    def set_fruit(self):
        """
        Sets the position of a new fruit on the game grid, if there are any free positions available.
        If there are no free positions available, sets the game status to 1 (win).

        Returns
        -------
        None
        """
        fp = self.free_positions
        if len(fp) != 0:
            self.fruit_position = np.random.choice(fp)
        else:
            self.status = 1

    def get_grid(self):
        """
        Get the numpy array that represents the current state of the game grid.
        This method updates the grid according to the current positions of the snake, forbidden cells, and the fruit.

        Returns:
        -------
        numpy.ndarray:
            The numpy array that represents the current state of the game grid.

        """

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
        """
        Check if the game is over due to a defeat condition, update the game status if necessary.
        If the snake occupies the same position as itself, the game is over and the status is updated to -1.
        If the snake occupies the same position as a forbidden position, the game is over and the status is updated to -2.

        Returns:
            None
        """
        # get forbidden positions and snake positions
        forbidden_positions = self.forbidden_positions
        snake_positions = self.snake_active_positions

        # check for self-collision
        if np.unique(snake_positions).size != snake_positions.size:
            self.status = -1

        # check for collision with forbidden positions
        if np.intersect1d(forbidden_positions, snake_positions).size != 0:
            self.status = -2

    def play(self, direction):
        """
        Update the state of the game based on the given direction.

        Parameters:
            direction (int): The direction the snake will move. Should be an integer in the range [0,3], where:
                0 = right
                1 = up
                2 = left
                3 = down

        Returns:
            status (int): The current status of the game. Should be an integer, where:
                0 = game still in progress
                -1 = snake collided with itself
                -2 = snake collided with forbidden positions
                -3 = invalid direction given
        """
        if self.status != 0:
            # If the game is already over, return the current status.
            return self.status
        else:
            # Otherwise, update the game state based on the input direction.
            snake_positions = self.snake_positions
            fruit_position = self.fruit_position
            head = snake_positions[0]
            neigh = get_neighbors(head, self.Nrow, self.Ncol)
            new_head = neigh[int(direction)]

            # Check if the new head would collide with the body of the snake.
            if new_head == snake_positions[1]:
                self.status = -1
            # Check if the new head is out of bounds.
            elif new_head < 0:
                self.status = -3
            else:
                # Update the snake's position.
                snake_positions[1:] = snake_positions[:-1]
                snake_positions[0] = new_head

                # If the snake eats a fruit, set a new fruit position and activate a new body segment.
                if new_head == fruit_position:
                    self.set_fruit()
                    sap = self.snake_active
                    sap[:] = np.roll(sap, 1)
                    sap[0] = True
                    self.score += 1

            # Check if the snake has collided with a forbidden position or with itself.
            self.check_defeat()

            # Return the updated game status.
            return self.status

    def turn(self, turn):
        """
        Turn the snake in a new direction.

        Parameters:
            turn (int): The direction to turn the snake. Should be an integer, where:
                0 = go forward
                1 = go left
                -1 = go right

        Returns:
            None

        """
        current_direction = self.get_current_direction()
        # Calculate the absolute direction
        abs_direction = (current_direction + turn) % 4
        # Call the play method with the new direction
        self.play(abs_direction)

    def get_current_direction(self):
        """
        Returns the current direction of the snake based on the positions of its head and neck.

        Returns:
            direction (int): An integer representing the current direction of the snake, where:
                0 = right
                1 = up
                2 = left
                3 = down
                -1 = if the direction could not be determined
        """
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

    def get_snake_direction_map(self):
        snake_map = {0: "right", 1: "up", 2: "left", 3: "down"}
        return snake_map[self.get_current_direction()]

    def get_fruit_relative_directions(self):
        """
        Calculate the relative directions of the fruit from the snake's head.

        Returns:
            acos (float): The cosine of the angle between the fruit and the x-axis, in radians.
            asin (float): The sine of the angle between the fruit and the y-axis, in radians.
        """
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

    def get_neighbors_pos(self):
        """
        Returns the positions of the three neighboring cells relative to the snake's head position.

        Returns:
            out (ndarray): A numpy array of shape (3,) containing the positions of the neighboring cells.
                The left, front and right neighboring cells are respectively located at index 0, 1 and 2
                of the returned array. Each position is represented by an integer value corresponding to
                the cell index in the flattened game grid.
        """

        Ncol = self.Ncol
        headpos = self.snake_active_positions[0]
        fdir = self.get_current_direction()

        # Calculate positions of the three neighboring positions
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

        return np.array([rightpos, frontpos, leftpos])

    def get_turn_neighbors(self):
        """
        Get the state of the neighboring positions relatively to snake head can turn to.
        Elements index correspond to the following directions: [left, forward, right].
        Possible element value are:
            1.0 = fruit present
            -1.0 = forbidden position (lava or snake tail)
            0.0 = nothing special present
        Returns:
            out (ndarray): A numpy array of shape (3,) representing the state of the neighboring positions.
        """
        forbidden_positions = self.forbidden_positions
        snake_tail_positions = self.snake_active_positions[1:]
        tail_and_lava = np.union1d(snake_tail_positions, forbidden_positions)
        fruit_position = self.fruit_position

        # Get the positions of the neighboring cells
        positions = self.get_neighbors_pos()

        # Calculate the relative direction of fruit and forbidden positions for each neighboring position
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
        Indicates the distance to the closest obstacle (lava or snake tail) in each direction (right, front and left) relatively to snake head.
        Returns:
            out (ndarray): A numpy array of shape (3,) representing the distance to the closest obstacle in each direction.
        """

        def _compute_distance(all_sidepos):
            for dist, sidepos in enumerate(all_sidepos):
                if sidepos in tail_and_lava:
                    return dist
                elif sidepos == fruit_position:
                    return self.Ncell

        Ncol = self.Ncol
        headpos = self.snake_active_positions[0]
        forbidden_positions = self.forbidden_positions
        snake_tail_positions = self.snake_active_positions[1:]
        tail_and_lava = np.union1d(snake_tail_positions, forbidden_positions)
        fruit_position = self.fruit_position
        fdir = self.get_current_direction()

        # Calculate positions of the three neighboring positions
        if fdir == 0:
            all_frontpos = np.arange(
                headpos + 1, ((headpos // self.Ncol + 1) * self.Ncol)
            )
            all_leftpos = np.arange(headpos - Ncol, -1, -Ncol)
            all_rightpos = np.arange(headpos + Ncol, self.Ncol**2, Ncol)
        if fdir == 1:
            all_frontpos = np.arange(headpos - Ncol, -1, -Ncol)
            all_leftpos = np.arange(
                headpos - 1, (headpos // self.Ncol) * self.Ncol - 1, -1
            )
            all_rightpos = np.arange(
                headpos + 1, (headpos // self.Ncol + 1) * self.Ncol
            )
        if fdir == 2:
            all_frontpos = np.arange(
                headpos - 1, (headpos // self.Ncol) * self.Ncol - 1, -1
            )
            all_leftpos = np.arange(headpos + Ncol, self.Ncol**2, Ncol)
            all_rightpos = np.arange(headpos - Ncol, -1, -Ncol)

        if fdir == 3:
            all_frontpos = np.arange(headpos + Ncol, self.Ncol**2, Ncol)
            all_leftpos = np.arange(headpos + 1, (headpos // self.Ncol + 1) * self.Ncol)
            all_rightpos = np.arange(
                headpos - 1, (headpos // self.Ncol) * self.Ncol - 1, -1
            )

        out = np.zeros(3)

        out[0] = _compute_distance(all_rightpos)
        out[1] = _compute_distance(all_frontpos)
        out[2] = _compute_distance(all_leftpos)

        return out

    def get_enhanched_lidar(self):
        """
        Indicates the distance to the closest obstacle (lava or snake tail) in each direction (right-back, right , front, left, left-back) relatively to snake head.
        Returns:
            out (ndarray): A numpy array of shape (5,) representing the distance to the closest obstacle in each direction.
        """

        def _compute_distance(all_sidepos):
            for dist, sidepos in enumerate(all_sidepos):
                if sidepos in tail_and_lava:
                    return dist
                elif sidepos == fruit_position:
                    return self.Ncell

        out = np.zeros(5)

        Ncol = self.Ncol
        headpos = self.snake_active_positions[0]
        forbidden_positions = self.forbidden_positions
        snake_tail_positions = self.snake_active_positions[1:]
        tail_and_lava = np.union1d(snake_tail_positions, forbidden_positions)
        fruit_position = self.fruit_position
        fdir = self.get_current_direction()

        # Calculate positions of the three neighboring positions
        out[1:4] = self.get_lidar()

        # Calculate positions of the two back neighboring positions
        if fdir == 0:
            all_back_leftpos = np.arange(headpos - Ncol - 1, -1, -Ncol - 1)
            all_back_rightpos = np.arange(headpos + Ncol - 1, self.Ncol**2, Ncol - 1)

        if fdir == 1:
            all_back_rightpos = np.arange(headpos + Ncol + 1, self.Ncol**2, Ncol + 1)
            all_back_leftpos = np.arange(headpos + Ncol - 1, self.Ncol**2, Ncol - 1)

        if fdir == 2:
            all_back_rightpos = np.arange(headpos - Ncol + 1, -1, -Ncol + 1)
            all_back_leftpos = np.arange(headpos + Ncol + 1, self.Ncol**2, Ncol + 1)

        if fdir == 3:
            all_back_rightpos = np.arange(headpos - Ncol - 1, -1, -Ncol - 1)
            all_back_leftpos = np.arange(headpos - Ncol + 1, -1, -Ncol + 1)

        out[0] = _compute_distance(all_back_rightpos)
        out[4] = _compute_distance(all_back_leftpos)

        return out

    def sensors(self, method="default"):
        """
        Returns sensor readings that an agent can use to make decisions based on the state of the game board.

        Args:
            method (str): The method to use for obtaining sensor readings. Default is "default".

        Returns:
            out (ndarray): An array of sensor readings.

        """
        if method == "default":
            # Use the default method to obtain sensor readings.
            out = np.zeros(5, dtype=np.float64)
            out[:3] = self.get_turn_neighbors()  # Get the turn neighbors.
            out[
                3:
            ] = (
                self.get_fruit_relative_directions()
            )  # Get the relative directions to the fruit.

        if method == "lidar":
            # Use the lidar method to obtain sensor readings.
            out = np.zeros(5, dtype=np.float64)
            out[:3] = self.get_lidar()  # Get the lidar readings.
            out[
                3:
            ] = (
                self.get_fruit_relative_directions()
            )  # Get the relative directions to the fruit.
        if method == "elidar":
            out = np.zeros(7, dtype=np.float64)
            out[:5] = self.get_enhanched_lidar()  # Get the lidar readings.
            out[
                -2:
            ] = (
                self.get_fruit_relative_directions()
            )  # Get the relative directions to the fruit.
            # print(f"Careful sensor readings array is of size {out.shape[0]}")

        return out

    def get_snake_metrics(self):
        """
        Returns the following metrics:
            - Snake length
            - Snake head position
            - n-1 neighboring status
            - Lidar
            - Enhanched lidar (add back neighbors)
        """

        def _get_snake_direction_map(neighbors_status):
            dir_list = ["right", "front", "left"]
            snake_map = {}
            for i in range(3):
                snake_map[dir_list[i]] = neighbors_status[i]
            return snake_map

        print(f"Snake length: {len(self.snake_active_positions)}")
        print(f"Snake head position: {self.snake_active_positions[0]}")
        print(
            f"Lv1 Neighbors status: {_get_snake_direction_map(self.get_turn_neighbors())}"
        )
        print(f"Lidar: {self.get_lidar()}")
        print(f"Enhanced Lidar: {self.get_enhanched_lidar()}")


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


def show_gui(snake, ax, return_metrics=False):
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
    # Add a standalone legend  gray box = head, black box = body, red box = wall, green box = fruit
    entries = {"Head": "gray", "Body": "black", "Wall": "red", "Fruit": "green"}

    f = lambda m, c: ax.plot([], [], marker=m, color=c, ls="none")[0]
    handles = [f("s", val) for key, val in entries.items()]
    labels = [key for key, val in entries.items()]
    ax.legend(handles, labels, loc=(1.1, 0), framealpha=1, frameon=False)

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
