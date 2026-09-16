#!/usr/bin/env python3
"""Run AI search performance benchmarks and display results."""

from chess_engine.AI.benchmarks import run_ai_benchmarks


def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_result(name, stats):
    label = name.replace("_", " ").title()
    print(f"  {label:<24} depth {stats.depth_reached:>2} | "
          f"{stats.total_nodes:>10,} nodes | "
          f"{stats.nodes_per_second:>10,} nodes/s | "
          f"{stats.time_seconds:>6.2f}s"
          f"{'  (timed out)' if stats.timed_out else ''}")


print_header("AI SEARCH BENCHMARKS")

results = run_ai_benchmarks(max_depth=5, time_limit=5.0)
for name, stats in results.items():
    print_result(name, stats)

print_header("BENCHMARK COMPLETE")
