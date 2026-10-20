"""Command-line entry point for the educational simulation."""

import argparse
import csv
from pathlib import Path

from .simulator import simulate


def save_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def save_plot(rows: list[dict], path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Plotting requires: pip install '.[plot]'") from exc

    t = [r["time_s"] for r in rows]
    fig, (a, b) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, layout="constrained")
    a.plot(t, [r["cabin_actual_c"] for r in rows], label="Simulated cabin temperature")
    a.plot(t, [r["target_cabin_c"] for r in rows], linestyle="--", label="Requested temperature")
    a.set_ylabel("Temperature (°C)")
    a.set_title("Original Climate Control Prototyping Demo (Synthetic Data)")
    a.legend(loc="best")
    a.grid(alpha=0.3)
    b.plot(t, [r["blend_command_pct"] for r in rows], label="Blend flap: command")
    b.plot(t, [r["blend_actual_pct"] for r in rows], label="Blend flap: simulated actual")
    if any(r["blend_mismatch_flag"] for r in rows):
        alarm_times = [r["time_s"] for r in rows if r["blend_mismatch_flag"]]
        b.axvspan(min(alarm_times), max(alarm_times), alpha=0.12, label="Mismatch warning")
    b.set_ylabel("Blend position (%)")
    b.set_xlabel("Elapsed time (s)")
    b.legend(loc="best")
    b.grid(alpha=0.3)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic automotive climate-control prototyping demo")
    parser.add_argument("--duration", type=int, default=360, help="Simulated seconds (default: 360)")
    parser.add_argument("--output", default="outputs/normal.csv", help="CSV destination")
    parser.add_argument("--plot", help="Optional PNG destination (requires matplotlib)")
    parser.add_argument("--stuck-blend", action="store_true", help="Inject a stuck temperature-blend flap")
    parser.add_argument("--fault-at", type=float, default=190.0, help="Fault time in seconds")
    args = parser.parse_args()

    rows = simulate(duration_s=args.duration, stuck_blend=args.stuck_blend, fault_at_s=args.fault_at)
    save_csv(rows, Path(args.output))
    if args.plot:
        save_plot(rows, Path(args.plot))
    print(f"Wrote {len(rows)} synthetic samples to {args.output}")
    print(f"Final cabin temperature: {rows[-1]['cabin_actual_c']:.2f} °C")
    print(f"Blend mismatch flagged: {any(r['blend_mismatch_flag'] for r in rows)}")


if __name__ == "__main__":
    main()
