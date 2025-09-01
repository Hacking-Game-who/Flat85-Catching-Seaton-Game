import argparse
import math
import random
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class AnchorPoint:
    x: float
    y: float
    signal: float


def get_screen_size() -> Tuple[int, int]:
    """Return the primary screen width and height in pixels.

    Uses Windows API via ctypes when available. Falls back to a common size if detection fails.
    """
    try:
        # Windows-specific via ctypes
        import ctypes  # type: ignore

        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        width = int(user32.GetSystemMetrics(0))
        height = int(user32.GetSystemMetrics(1))
        if width > 0 and height > 0:
            return width, height
    except Exception:
        # Fallback below
        pass

    # Generic fallback
    return 1920, 1080


def parse_points_arg(points_arg: str) -> List[AnchorPoint]:
    """Parse --points argument formatted as
    "x1,y1,s1;x2,y2,s2;x3,y3,s3;x4,y4,s4".
    """
    parts = [p.strip() for p in points_arg.split(";") if p.strip()]
    if len(parts) != 4:
        raise ValueError("--points must contain exactly 4 triplets separated by ';'")

    anchors: List[AnchorPoint] = []
    for part in parts:
        coords = [c.strip() for c in part.replace(" ", "").split(",") if c.strip()]
        if len(coords) != 3:
            raise ValueError("Each triplet must be in the form x,y,signal")
        x_str, y_str, s_str = coords
        anchors.append(AnchorPoint(float(x_str), float(y_str), float(s_str)))
    return anchors


def read_points_interactive() -> List[AnchorPoint]:
    """Interactively read 4 points (x, y, signal) from stdin."""
    print("Please enter 4 points (one per line) in the format: x y signal")
    anchors: List[AnchorPoint] = []
    for i in range(4):
        while True:
            try:
                line = input(f"Point {i + 1}: ").strip()
                if not line:
                    continue
                tokens = [t for t in line.split() if t]
                if len(tokens) != 3:
                    print("Invalid format. Please enter: x y signal")
                    continue
                x_val = float(tokens[0])
                y_val = float(tokens[1])
                s_val = float(tokens[2])
                anchors.append(AnchorPoint(x_val, y_val, s_val))
                break
            except ValueError:
                print("Parse failed. Please try again. Example: 100.0 200.0 0.8")
    return anchors


def compute_best_scale_and_error(candidate_x: float, candidate_y: float, anchors: List[AnchorPoint]) -> Tuple[float, float]:
    """For a candidate point, compute the least-squares scale k and the squared error.

    We minimize sum_i (d_i - k * s_i)^2 where d_i is the Euclidean distance from the candidate
    point to anchor i, and s_i is the signal value. The optimal k is:
        k = (sum_i d_i * s_i) / (sum_i s_i^2)
    If sum_i s_i^2 == 0, set k = 0 and error = sum_i d_i^2.
    Returns (k, squared_error).
    """
    distances: List[float] = []
    signals: List[float] = []
    for anchor in anchors:
        dx = candidate_x - anchor.x
        dy = candidate_y - anchor.y
        distance = math.hypot(dx, dy)
        distances.append(distance)
        signals.append(anchor.signal)

    sum_ss = sum(s * s for s in signals)
    if sum_ss == 0.0:
        # Degenerate case: all signals are zero -> k=0, error=sum d^2
        squared_error = sum(d * d for d in distances)
        return 0.0, squared_error

    sum_ds = sum(d * s for d, s in zip(distances, signals))
    k = sum_ds / sum_ss
    squared_error = sum((d - k * s) ** 2 for d, s in zip(distances, signals))
    return k, squared_error


def monte_carlo_search(
    anchors: List[AnchorPoint],
    num_samples: int,
    screen_width: int,
    screen_height: int,
    rng: random.Random,
) -> Tuple[float, float, float, float]:
    """Run Monte Carlo search over the screen rectangle to find the best point.

    Returns (best_x, best_y, best_k, best_error).
    """
    best_x: Optional[float] = None
    best_y: Optional[float] = None
    best_k: Optional[float] = None
    best_error: float = float("inf")

    for _ in range(num_samples):
        x = rng.uniform(0.0, float(screen_width))
        y = rng.uniform(0.0, float(screen_height))
        k, err = compute_best_scale_and_error(x, y, anchors)
        if err < best_error:
            best_error = err
            best_x = x
            best_y = y
            best_k = k

    assert best_x is not None and best_y is not None and best_k is not None
    return best_x, best_y, best_k, best_error


def validate_anchors_within_screen(anchors: List[AnchorPoint], width: int, height: int) -> None:
    """Warn if any anchor is out of the screen bounds."""
    out_of_bounds = []
    for idx, a in enumerate(anchors):
        if not (0.0 <= a.x <= width and 0.0 <= a.y <= height):
            out_of_bounds.append(idx + 1)
    if out_of_bounds:
        print(
            f"Warning: Points {out_of_bounds} are out of screen bounds [0,{width}]x[0,{height}].",
            file=sys.stderr,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Monte Carlo search over screen area to find a coordinate where distances to four points are proportional to their signals."
        )
    )
    parser.add_argument(
        "--points",
        type=str,
        default=None,
        help=(
            "Four points in the format: 'x1,y1,s1;x2,y2,s2;x3,y3,s3;x4,y4,s4'. If omitted, interactive input is used."
        ),
    )
    parser.add_argument(
        "--num",
        type=int,
        default=10000,
        help="Number of Monte Carlo samples (default: 10000)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.seed is not None:
        rng = random.Random(args.seed)
    else:
        rng = random.Random()

    if args.points:
        anchors = parse_points_arg(args.points)
    else:
        # If stdin is not a TTY (e.g., piped), try to read 4 lines automatically
        if not sys.stdin.isatty():
            lines = [line.strip() for line in sys.stdin.readlines() if line.strip()]
            if len(lines) >= 4:
                parsed: List[AnchorPoint] = []
                for i in range(4):
                    tokens = [t for t in lines[i].split() if t]
                    if len(tokens) != 3:
                        raise ValueError(
                            "Failed to read from stdin: need 4 lines, each 'x y signal'"
                        )
                    parsed.append(
                        AnchorPoint(float(tokens[0]), float(tokens[1]), float(tokens[2]))
                    )
                anchors = parsed
            else:
                anchors = read_points_interactive()
        else:
            anchors = read_points_interactive()

    if len(anchors) != 4:
        raise ValueError("Exactly 4 points must be provided")

    width, height = get_screen_size()
    validate_anchors_within_screen(anchors, width, height)

    best_x, best_y, best_k, best_error = monte_carlo_search(
        anchors=anchors,
        num_samples=max(1, int(args.num)),
        screen_width=width,
        screen_height=height,
        rng=rng,
    )

    print("— Results —")
    print(f"Screen size: {width} x {height}")
    print("Input points (with signal):")
    for i, a in enumerate(anchors, start=1):
        print(f"  Point {i}: (x={a.x:.3f}, y={a.y:.3f}), signal={a.signal:.6f}")
    print(f"Samples: {args.num}")
    print(f"Best coordinate: (x={best_x:.6f}, y={best_y:.6f})")
    print(f"Best proportional scale k: {best_k:.9f}")
    print(f"Fit error (sum of squares): {best_error:.9f}")


if __name__ == "__main__":
    main()
