from matplotlib import pyplot as plt
import snakelib as snklib
import numpy as np


def plot_grid(snake):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    grid_img = np.ones_like(snake.all_positions.reshape(snake.Nrow, snake.Ncol))
    plt.imshow(
        grid_img, cmap="binary", origin="upper", extent=[0, snake.Nrow, 0, snake.Ncol]
    )
    for l in range(snake.Nrow):
        for c in range(snake.Ncol):
            z = snake.all_positions.reshape(snake.Nrow, snake.Ncol)[l, c]
            xc = snake.Nrow - 1 - l
            yc = c
            plt.text(yc + 0.5, xc + 0.5, str(z), va="center", ha="center", fontsize=12)

    for g in range(snake.Nrow + 1):
        plt.plot(
            np.linspace(0, snake.Nrow, num=snake.Nrow + 1),
            np.ones(snake.Nrow + 1) * g,
            "r-",
            linewidth=2,
        )
        plt.plot(
            np.ones(snake.Nrow + 1) * g,
            np.linspace(0, snake.Nrow, num=snake.Nrow + 1),
            "r-",
            linewidth=2,
        )

    for g in range(1, snake.Nrow):
        plt.plot(
            np.linspace(1, snake.Nrow - 1, num=snake.Nrow),
            np.ones(snake.Nrow) * g,
            "g-",
            linewidth=2,
        )
        plt.plot(
            np.ones(snake.Nrow) * g,
            np.linspace(1, snake.Nrow - 1, num=snake.Nrow),
            "g-",
            linewidth=2,
        )

    entries = {"Lava": "red", "Playground": "green"}
    f = lambda m, c: ax.plot([], [], marker=m, color=c, ls="none")[0]
    handles = [f("s", val) for key, val in entries.items()]
    labels = [key for key, val in entries.items()]
    plt.legend(handles, labels, loc=(1.1, 0), framealpha=1, frameon=False)

    plt.title("Game grid")
    plt.xlabel("Nrow")
    plt.ylabel("Ncol")
    plt.show()


def plot_snake(snake):
    """ """

    grid_img = np.ones([snake.Nrow, snake.Ncol, 3], dtype=np.uint8) * 255

    # Converting to grid coordinates
    # Snake
    snake_grid_coor = np.array(
        snklib.pos_to_coords(snake.snake_active_positions, Ncol=snake.Ncol)
    ).T.reshape(-1, snake.snake_active_positions.shape[0])
    # Fruit
    fruit_grid_coor = np.array(snklib.pos_to_coords(snake.fruit_position, snake.Ncol))

    # Neighbors
    neighbors_grid_coor = np.array(
        snklib.pos_to_coords(snake.get_neighbors_pos(), Ncol=snake.Ncol)
    ).T.reshape(-1, snake.snake_active_positions.shape[0])

    # Coloring the snake
    for ind, sc in enumerate(snake_grid_coor):
        if ind == 0:
            grid_img[sc[0], sc[1], :] = 191
        else:
            grid_img[sc[0], sc[1], :] = 118

    # Coloring fruit
    grid_img[fruit_grid_coor[0], fruit_grid_coor[1], 1] = 25
    grid_img[fruit_grid_coor[0], fruit_grid_coor[1], 2] = 200

    # Coloring the neighbors
    for ind, sc in enumerate(neighbors_grid_coor):
        grid_img[sc[0], sc[1], 0] = 25
        grid_img[sc[0], sc[1], 2] = 25

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.imshow(grid_img, origin="upper", extent=[0, snake.Nrow, 0, snake.Ncol])
    for l in range(snake.Nrow):
        for c in range(snake.Ncol):
            z = snake.all_positions.reshape(snake.Nrow, snake.Ncol)[l, c]
            xc = snake.Nrow - 1 - l
            yc = c
            plt.text(yc + 0.5, xc + 0.5, str(z), va="center", ha="center", fontsize=12)

    for g in range(snake.Nrow + 1):
        plt.plot(
            np.linspace(0, snake.Nrow, num=snake.Nrow + 1),
            np.ones(snake.Nrow + 1) * g,
            "r-",
            linewidth=2,
        )
        plt.plot(
            np.ones(snake.Nrow + 1) * g,
            np.linspace(0, snake.Nrow, num=snake.Nrow + 1),
            "r-",
            linewidth=2,
        )

    for g in range(1, snake.Nrow):
        plt.plot(
            np.linspace(1, snake.Nrow - 1, num=snake.Nrow),
            np.ones(snake.Nrow) * g,
            "g-",
            linewidth=2,
        )
        plt.plot(
            np.ones(snake.Nrow) * g,
            np.linspace(1, snake.Nrow - 1, num=snake.Nrow),
            "g-",
            linewidth=2,
        )

    entries = {
        "Lava": "red",
        "Playground": "green",
        "Head": "#BFBFBF",
        "Body": "#767676",
        "Fruit": "#FF19C8",
        "Neighbors": "#19FF19",
    }
    f = lambda m, c: ax.plot([], [], marker=m, color=c, ls="none")[0]
    handles = [f("s", val) for key, val in entries.items()]
    labels = [key for key, val in entries.items()]
    plt.legend(handles, labels, loc=(1.1, 0), framealpha=1, frameon=False)

    plt.title("Snake directions")
    plt.xlabel("Nrow")
    plt.ylabel("Ncol")
    plt.show()


def plot_snake_theta(snake):
    grid_img = np.ones([snake.Nrow, snake.Ncol, 3], dtype=np.uint8) * 255

    # Converting to grid coordinates
    # Snake
    snake_grid_coor = np.array(
        snklib.pos_to_coords(snake.snake_active_positions, Ncol=snake.Ncol)
    ).T.reshape(-1, snake.snake_active_positions.shape[0])
    # Fruit
    fruit_grid_coor = np.array(snklib.pos_to_coords(snake.fruit_position, snake.Ncol))

    # Neighbors
    neighbors_grid_coor = np.array(
        snklib.pos_to_coords(snake.get_neighbors_pos(), Ncol=snake.Ncol)
    ).T.reshape(-1, snake.snake_active_positions.shape[0])

    # Coloring the snake
    for ind, sc in enumerate(snake_grid_coor):
        if ind == 0:
            grid_img[sc[0], sc[1], :] = 191
        else:
            grid_img[sc[0], sc[1], :] = 118

    # Coloring fruit
    grid_img[fruit_grid_coor[0], fruit_grid_coor[1], 1] = 25
    grid_img[fruit_grid_coor[0], fruit_grid_coor[1], 2] = 200

    # Coloring the neighbors
    for ind, sc in enumerate(neighbors_grid_coor):
        grid_img[sc[0], sc[1], 0] = 25
        grid_img[sc[0], sc[1], 2] = 25

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.imshow(grid_img, origin="upper", extent=[0, snake.Nrow, 0, snake.Ncol])
    for l in range(snake.Nrow):
        for c in range(snake.Ncol):
            z = snake.all_positions.reshape(snake.Nrow, snake.Ncol)[l, c]
            z = ""
            xc = snake.Nrow - 1 - l
            yc = c
            plt.text(yc + 0.5, xc + 0.5, str(z), va="center", ha="center", fontsize=12)

    for g in range(snake.Nrow + 1):
        plt.plot(
            np.linspace(0, snake.Nrow, num=snake.Nrow + 1),
            np.ones(snake.Nrow + 1) * g,
            "r-",
            linewidth=2,
        )
        plt.plot(
            np.ones(snake.Nrow + 1) * g,
            np.linspace(0, snake.Nrow, num=snake.Nrow + 1),
            "r-",
            linewidth=2,
        )

    for g in range(1, snake.Nrow):
        plt.plot(
            np.linspace(1, snake.Nrow - 1, num=snake.Nrow),
            np.ones(snake.Nrow) * g,
            "g-",
            linewidth=2,
        )
        plt.plot(
            np.ones(snake.Nrow) * g,
            np.linspace(1, snake.Nrow - 1, num=snake.Nrow),
            "g-",
            linewidth=2,
        )

    u = np.array([[4.5, 6.5], [7.5, 6.5]])

    plt.plot(u[:, 0], u[:, 1], "-b", lw=2)

    v = np.array([[4.5, 6.5], [6.5, 4.5]])
    plt.plot(v[:, 0], v[:, 1], "-r", lw=2)

    # Draw a arc circle with center (x,y) and radius r
    def draw_arc(x, y, r, start_angle, end_angle):
        theta = np.linspace(start_angle, end_angle, 100)
        x1 = x + r * np.cos(theta)
        y1 = y + r * np.sin(theta)
        plt.plot(x1, y1, "--k", lw=2)

    draw_arc(4.5, 6.5, 3, 0, -np.pi / 4)
    plt.text(7.5, 4.5, r"$\theta$", fontdict={"size": 20})

    entries = {
        "Lava": "red",
        "Playground": "green",
        "Head": "#BFBFBF",
        "Body": "#767676",
        "Fruit": "#FF19C8",
        "Neighbors": "#19FF19",
    }
    f = lambda m, c: ax.plot([], [], marker=m, color=c, ls="none")[0]
    handles = [f("s", val) for key, val in entries.items()]
    labels = [key for key, val in entries.items()]
    plt.legend(handles, labels, loc=(1.1, 0), framealpha=1, frameon=False)

    plt.title(r"$\Theta$ angle")
    plt.xlabel("Nrow")
    plt.ylabel("Ncol")
    plt.show()
