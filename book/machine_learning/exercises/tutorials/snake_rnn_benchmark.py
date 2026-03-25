#!/usr/bin/env python3
"""
Benchmark genetic training for recurrent neural Snake agents.

Examples
--------
python book/machine_learning/exercises/tutorials/snake_rnn_benchmark.py
python book/machine_learning/exercises/tutorials/snake_rnn_benchmark.py --configs compact-rnn,egocentric-r4-rnn
python book/machine_learning/exercises/tutorials/snake_rnn_benchmark.py --rows 12 --cols 12 --population 60 --generations 12
"""

from __future__ import annotations

import argparse
import time

import numpy as np

from snakelib import FastSnake, RecurrentNeuralAgent, RecurrentPolicyAgent


CONFIG_PRESETS = {
    "default-rnn": {
        "sensor_method": "default",
        "sensor_kwargs": {},
        "memory_size": 4,
        "hidden_sizes": (8,),
    },
    "compact-rnn": {
        "sensor_method": "compact",
        "sensor_kwargs": {},
        "memory_size": 4,
        "hidden_sizes": (8,),
    },
    "compact-rnn-m8": {
        "sensor_method": "compact",
        "sensor_kwargs": {},
        "memory_size": 8,
        "hidden_sizes": (8,),
    },
    "egocentric-r4-rnn": {
        "sensor_method": "egocentric",
        "sensor_kwargs": {"radius": 4},
        "memory_size": 4,
        "hidden_sizes": (8,),
    },
}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--configs",
        default="compact-rnn,default-rnn,compact-rnn-m8,egocentric-r4-rnn",
        help=f"Comma-separated configuration names. Available: {', '.join(CONFIG_PRESETS)}",
    )
    parser.add_argument("--rows", type=int, default=10, help="Grid row count.")
    parser.add_argument("--cols", type=int, default=10, help="Grid column count.")
    parser.add_argument(
        "--population", type=int, default=40, help="Population size for evolution."
    )
    parser.add_argument(
        "--generations", type=int, default=8, help="Number of generations."
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=3,
        help="Training episodes per individual and per generation.",
    )
    parser.add_argument(
        "--eval-episodes",
        type=int,
        default=8,
        help="Evaluation episodes for the final champion.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Maximum turns per episode. Default: 4 * Ncell.",
    )
    parser.add_argument("--keep-ratio", type=float, default=0.2)
    parser.add_argument("--mutation-ratio", type=float, default=0.35)
    parser.add_argument("--mutation-sigma", type=float, default=0.15)
    parser.add_argument(
        "--init-sigma",
        type=float,
        default=0.5,
        help="Initial Gaussian standard deviation for weights.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed.")
    return parser


def fruit_distance(snake):
    head_row, head_col = snake.head_coords
    fruit_row, fruit_col = snake.pos_to_coords(snake.fruit_position)
    return abs(fruit_row - head_row) + abs(fruit_col - head_col)


def episode_metrics(snake, agent, max_turns=None, fix_seed=None):
    snake.reset(fix_seed=fix_seed)
    agent.reset()
    if max_turns is None:
        max_turns = 4 * snake.Ncell

    turns = 0
    progress = 0.0
    previous_distance = fruit_distance(snake)
    while snake.status == 0 and turns < max_turns:
        score_before = snake.score
        snake.turn(agent(snake))
        turns += 1

        if snake.status != 0:
            break

        current_distance = fruit_distance(snake)
        if snake.score > score_before:
            progress += 1.0
            previous_distance = current_distance
        else:
            progress += (
                previous_distance - current_distance
            ) / snake.max_manhattan_distance
            previous_distance = current_distance

    fitness = snake.score * 1000.0 + progress * 25.0 - turns * 0.1
    return {
        "score": float(snake.score),
        "turns": float(turns),
        "progress": float(progress),
        "fitness": float(fitness),
        "won": float(snake.status == 1),
    }


def evaluate_weights(
    weights,
    rows,
    cols,
    sensor_method,
    sensor_kwargs,
    memory_size,
    hidden_sizes,
    episodes,
    max_turns,
    seed,
):
    snake = FastSnake(rows, cols)
    observation_size = snake.sensors(method=sensor_method, **sensor_kwargs).size
    network = RecurrentNeuralAgent(
        weights=weights,
        observation_size=observation_size,
        memory_size=memory_size,
        hidden_sizes=hidden_sizes,
        action_size=3,
    )
    agent = RecurrentPolicyAgent(
        network,
        sensor_method=sensor_method,
        sensor_kwargs=sensor_kwargs,
    )

    metrics = []
    for episode_id in range(episodes):
        metrics.append(
            episode_metrics(
                snake,
                agent,
                max_turns=max_turns,
                fix_seed=seed + episode_id,
            )
        )

    return {
        "mean_score": float(np.mean([item["score"] for item in metrics])),
        "max_score": int(np.max([item["score"] for item in metrics], initial=0)),
        "mean_turns": float(np.mean([item["turns"] for item in metrics])),
        "mean_progress": float(np.mean([item["progress"] for item in metrics])),
        "mean_fitness": float(np.mean([item["fitness"] for item in metrics])),
        "win_rate": float(np.mean([item["won"] for item in metrics])),
        "raw": metrics,
    }


def train_configuration(
    name,
    config,
    rows,
    cols,
    population_size,
    generations,
    trials,
    eval_episodes,
    max_turns,
    keep_ratio,
    mutation_ratio,
    mutation_sigma,
    init_sigma,
    seed,
):
    rng = np.random.default_rng(seed)
    snake = FastSnake(rows, cols)
    observation_size = snake.sensors(
        method=config["sensor_method"], **config["sensor_kwargs"]
    ).size
    weight_count = RecurrentNeuralAgent.count_weights(
        observation_size=observation_size,
        memory_size=config["memory_size"],
        hidden_sizes=config["hidden_sizes"],
        action_size=3,
    )

    population = rng.normal(
        loc=0.0,
        scale=init_sigma,
        size=(population_size, weight_count),
    )
    keep_count = max(2, int(round(keep_ratio * population_size)))
    best_weights = population[0].copy()
    best_fitness = -np.inf
    history = []

    start = time.perf_counter()
    for generation in range(generations):
        scores = np.zeros(population_size, dtype=np.float64)
        turns = np.zeros(population_size, dtype=np.float64)
        progress = np.zeros(population_size, dtype=np.float64)
        fitness = np.zeros(population_size, dtype=np.float64)

        for individual_id in range(population_size):
            metrics = evaluate_weights(
                population[individual_id],
                rows=rows,
                cols=cols,
                sensor_method=config["sensor_method"],
                sensor_kwargs=config["sensor_kwargs"],
                memory_size=config["memory_size"],
                hidden_sizes=config["hidden_sizes"],
                episodes=trials,
                max_turns=max_turns,
                seed=seed + 1000 * generation + 37 * individual_id,
            )
            scores[individual_id] = metrics["mean_score"]
            turns[individual_id] = metrics["mean_turns"]
            progress[individual_id] = metrics["mean_progress"]
            fitness[individual_id] = metrics["mean_fitness"]

        order = np.argsort(fitness)[::-1]
        champion_id = int(order[0])
        champion_fitness = float(fitness[champion_id])
        champion_score = float(scores[champion_id])
        history.append((champion_fitness, champion_score))

        if champion_fitness > best_fitness:
            best_fitness = champion_fitness
            best_weights = population[champion_id].copy()

        next_population = np.empty_like(population)
        next_population[:keep_count] = population[order[:keep_count]]

        for individual_id in range(keep_count, population_size):
            parent_ids = rng.choice(keep_count, size=2, replace=False)
            alpha = rng.random(weight_count)
            child = next_population[parent_ids[0]] * alpha + next_population[
                parent_ids[1]
            ] * (1.0 - alpha)
            if rng.random() < mutation_ratio:
                child += rng.normal(loc=0.0, scale=mutation_sigma, size=weight_count)
            next_population[individual_id] = child

        population = next_population

    elapsed = time.perf_counter() - start
    final_eval = evaluate_weights(
        best_weights,
        rows=rows,
        cols=cols,
        sensor_method=config["sensor_method"],
        sensor_kwargs=config["sensor_kwargs"],
        memory_size=config["memory_size"],
        hidden_sizes=config["hidden_sizes"],
        episodes=eval_episodes,
        max_turns=max_turns,
        seed=seed + 999_999,
    )

    return {
        "name": name,
        "sensor_method": config["sensor_method"],
        "sensor_kwargs": config["sensor_kwargs"],
        "memory_size": config["memory_size"],
        "hidden_sizes": config["hidden_sizes"],
        "observation_size": int(observation_size),
        "weight_count": int(weight_count),
        "best_fitness": float(best_fitness),
        "final_mean_score": float(final_eval["mean_score"]),
        "final_max_score": int(final_eval["max_score"]),
        "final_mean_turns": float(final_eval["mean_turns"]),
        "final_win_rate": float(final_eval["win_rate"]),
        "elapsed": float(elapsed),
        "history": history,
    }


def format_summary_table(results):
    headers = (
        "config",
        "sensor",
        "obs",
        "mem",
        "params",
        "best_fit",
        "mean_score",
        "max_score",
        "mean_turns",
        "time_s",
    )
    rows = [headers]
    for result in results:
        rows.append(
            (
                result["name"],
                result["sensor_method"],
                str(result["observation_size"]),
                str(result["memory_size"]),
                str(result["weight_count"]),
                f"{result['best_fitness']:.1f}",
                f"{result['final_mean_score']:.2f}",
                str(result["final_max_score"]),
                f"{result['final_mean_turns']:.1f}",
                f"{result['elapsed']:.2f}",
            )
        )

    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    lines = []
    for row_id, row in enumerate(rows):
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
        if row_id == 0:
            lines.append("  ".join("-" * widths[i] for i in range(len(headers))))
    return "\n".join(lines)


def main():
    args = build_parser().parse_args()
    config_names = [name.strip() for name in args.configs.split(",") if name.strip()]

    unknown = [name for name in config_names if name not in CONFIG_PRESETS]
    if unknown:
        raise SystemExit(f"Unknown config(s): {', '.join(unknown)}")

    max_turns = args.max_turns
    if max_turns is None:
        max_turns = 4 * args.rows * args.cols

    results = []
    for config_index, name in enumerate(config_names):
        result = train_configuration(
            name=name,
            config=CONFIG_PRESETS[name],
            rows=args.rows,
            cols=args.cols,
            population_size=args.population,
            generations=args.generations,
            trials=args.trials,
            eval_episodes=args.eval_episodes,
            max_turns=max_turns,
            keep_ratio=args.keep_ratio,
            mutation_ratio=args.mutation_ratio,
            mutation_sigma=args.mutation_sigma,
            init_sigma=args.init_sigma,
            seed=args.seed + 10_000 * config_index,
        )
        results.append(result)

    print(f"Environment: {args.rows} x {args.cols}")
    print(
        f"Population: {args.population}, generations: {args.generations}, trials: {args.trials}"
    )
    print(f"Evaluation episodes: {args.eval_episodes}, max turns: {max_turns}")
    print()
    print(format_summary_table(results))


if __name__ == "__main__":
    main()
