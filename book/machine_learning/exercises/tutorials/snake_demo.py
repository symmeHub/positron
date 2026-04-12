#!/usr/bin/env python3
"""
Benchmark and demonstration script for the refactored snake module.

Examples
--------
python book/machine_learning/exercises/tutorials/snake_demo.py
python book/machine_learning/exercises/tutorials/snake_demo.py --rows 12 --cols 12 --episodes 20
python book/machine_learning/exercises/tutorials/snake_demo.py --agent safe --episodes 5 --max-turns 500
"""

from __future__ import annotations

import argparse
import time

from snakelib import FastSnake, RandomTurnAgent, SafePathAgent, benchmark_agent


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--agent",
        choices=("random", "safe", "both"),
        default="both",
        help="Agent to benchmark.",
    )
    parser.add_argument("--rows", type=int, default=10, help="Grid row count.")
    parser.add_argument("--cols", type=int, default=10, help="Grid column count.")
    parser.add_argument(
        "--episodes", type=int, default=10, help="Number of episodes per benchmark."
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Maximum number of turns per episode. Default: 4 * Ncell.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed.")
    parser.add_argument(
        "--radius",
        type=int,
        default=2,
        help="Radius used to showcase the lightweight local observation.",
    )
    return parser


def print_environment_summary(rows, cols, radius):
    snake = FastSnake(rows, cols)
    compact = snake.sensors(method="compact")
    local_lite = snake.local_egocentric_channels_lite(radius=radius)

    print(f"Environment: {rows} x {cols}")
    print(f"Default sensor shape: {snake.sensors(method='default').shape}")
    print(f"Compact sensor shape: {compact.shape}")
    print(f"Local lite shape: {snake.sensors(method='local_lite').shape}")
    print(f"Local lite tensor shape (radius={radius}): {local_lite.shape}")
    print()


def print_stats(agent_name, stats, elapsed):
    print(f"{agent_name} agent")
    print(f"  episodes   : {stats['episodes']}")
    print(f"  mean score : {stats['mean_score']:.2f}")
    print(f"  max score  : {stats['max_score']}")
    print(f"  mean turns : {stats['mean_turns']:.2f}")
    print(f"  win rate   : {stats['win_rate']:.2%}")
    print(f"  wall time  : {elapsed:.3f} s")
    print()


def run_benchmark(agent_name, rows, cols, episodes, max_turns, seed):
    if agent_name == "random":
        agent = RandomTurnAgent()
    else:
        agent = SafePathAgent()

    start = time.perf_counter()
    stats = benchmark_agent(
        agent,
        Nrow=rows,
        Ncol=cols,
        episodes=episodes,
        max_turns=max_turns,
        seed=seed,
    )
    elapsed = time.perf_counter() - start
    print_stats(agent_name, stats, elapsed)


def main():
    args = build_parser().parse_args()
    print_environment_summary(args.rows, args.cols, args.radius)

    if args.agent in ("random", "both"):
        run_benchmark(
            "random",
            rows=args.rows,
            cols=args.cols,
            episodes=args.episodes,
            max_turns=args.max_turns,
            seed=args.seed,
        )

    if args.agent in ("safe", "both"):
        run_benchmark(
            "safe",
            rows=args.rows,
            cols=args.cols,
            episodes=args.episodes,
            max_turns=args.max_turns,
            seed=args.seed,
        )


if __name__ == "__main__":
    main()
