"""Command-line interface: turn a photo into a prime number portrait."""

import argparse
import sys

from .imaging import default_output_path, fit_palette, load_image, render_portrait
from .search import search_prime_portrait


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prime-portrait",
        description=(
            "Turn a photo into a 'prime portrait': a picture whose pixels are "
            "the digits of a (probable) prime number."
        ),
    )
    parser.add_argument("image", help="path to the input photo (any common format)")
    parser.add_argument(
        "--resize-factor",
        type=int,
        default=16,
        help="divide each image side by this; one digit per remaining pixel (default: 16)",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=10,
        help="number of colors/digits to quantize to, 2-10 (default: 10)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=None,
        help="worker processes for the search (default: all CPUs)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=40,
        help="Miller-Rabin rounds; error probability is at most 4**-trials (default: 40)",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=1_000_000,
        help="give up after this many candidate grids (default: 1000000)",
    )
    parser.add_argument("--font", default=None, help="path to a TrueType font for the digits")
    parser.add_argument(
        "--cell-size",
        type=int,
        default=32,
        help="output pixels per digit cell (default: 32)",
    )
    parser.add_argument(
        "--output", "-o", default=None, help="output PNG path (default: <image>-prime.png)"
    )
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    parser.add_argument(
        "--show", action="store_true", help="open the result in an image viewer when done"
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="suppress progress output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    say = (lambda *a, **k: None) if args.quiet else print

    try:
        image = load_image(args.image, args.resize_factor)
    except (OSError, ValueError) as exc:
        print(f"error: could not load {args.image!r}: {exc}", file=sys.stderr)
        return 1

    height, width = image.shape[:2]
    say(f"Digit grid: {width} x {height} = {width * height} digits")
    say(f"Quantizing to {args.clusters} colors...")
    kmeans = fit_palette(image, args.clusters, random_state=args.seed)

    say("Searching for a prime (this can take a while for large grids)...")
    result = search_prime_portrait(
        image,
        kmeans,
        threads=args.threads,
        trials=args.trials,
        max_attempts=args.max_attempts,
        seed=args.seed,
        progress=None if args.quiet else print,
    )
    if result is None:
        print(
            f"error: no prime found in {args.max_attempts} attempts; "
            "try again or use a different image",
            file=sys.stderr,
        )
        return 1

    say(
        f"\nFound a probable prime after {result.attempts} attempts "
        f"({result.seconds:.1f}s). Its {len(result.digits)} digits:\n"
    )
    say("\n".join(result.digit_rows()))

    output = args.output or default_output_path(args.image)
    portrait = render_portrait(result.grid, kmeans, font_path=args.font, cell_size=args.cell_size)
    portrait.save(output)
    say(f"\nSaved portrait to {output}")
    if args.show:
        portrait.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
