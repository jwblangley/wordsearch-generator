import argparse
import random

from typing import Callable


def grid_to_tex(grid: list[list[str]], included_words: list[str]) -> str:
    return (
        r"""
\documentclass[12pt]{article}

\usepackage[a4paper, margin=2cm]{geometry}
\usepackage{array}

\renewcommand{\familydefault}{\sfdefault}

\begin{document}

\noindent
\begin{center}
\begin{tabular}{| """
        + r"p{1em}" * len(grid[0])
        + r""" |}
    \hline
"""
        + "\n".join(("    " + " & ".join(l) + " \\\\\n") for l in grid)
        + r"""
    \hline
\end{tabular}
\end{center}

\end{document}
"""
    )

def generate_grid(width: int, height: int, wordlist: list[str], target_fill_rate:float=0.4, give_up_rate:float=0.01) -> list[list[str]]:
    grid = [[" " for _ in range(width)] for _ in range(height)]
    max_word_len = max(width, height)

    # Start with largest_words - easier to fit earlier
    wordlist = list(sorted((w for w in wordlist if len(w) <= max_word_len), key=(lambda w: len(w)), reverse=True))

    # Randomly select words
    mean_word_len = sum(len(w) for w in wordlist) / len(wordlist)
    mean_num_fit = (width * height) / mean_word_len
    heuristic_rate = target_fill_rate * (mean_num_fit / len(wordlist))

    # Start at 1 to keep maths valid: skew is negligble for large numbers
    attempts = 1
    successes = 1
    word_iter = iter(w for w in wordlist if random.random() < heuristic_rate)

    word_to_fit = next(word_iter, None)

    while successes / attempts > give_up_rate and word_to_fit is not None:
        attempts += 1

        direction_x = random.choice([-1, 0, 1])
        direction_y = random.choice([-1, 1] + ([0] if direction_x != 0 else []))

        if direction_x == 0:
            start_range_x = range(0, width)
        elif direction_x == 1:
            start_range_x = range(0, width - len(word_to_fit))
        else:
            start_range_x = range(width - 1, width - len(word_to_fit), -1)

        if direction_y == 0:
            start_range_y = range(0, height)
        elif direction_y == 1:
            start_range_y = range(0, height - len(word_to_fit))
        else:
            start_range_y = range(height - 1, height - len(word_to_fit), -1)

        try:
            start_x = random.choice(start_range_x)
            start_y = random.choice(start_range_y)
        except IndexError:
            # If possible range is empty
            continue

        x = start_x
        y = start_y

        for i in range(len(word_to_fit)):
            if not (0 <= x < width and 0 <= y < height):
                # Ran out of bounds
                break

            if grid[y][x] != " " and grid[y][x] != word_to_fit[i]:
                # Doesn't fit
                break
            x += direction_x
            y += direction_y
        else:
            x = start_x
            y = start_y
            for i in range(len(word_to_fit)):
                grid[y][x] = word_to_fit[i]
                x += direction_x
                y += direction_y
            successes += 1
            word_to_fit = next(word_iter, None)

    for y in range(height):
        for x in range(width):
            if grid[y][x] == " ":
                grid[y][x] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return grid

def _arg_int_range(low: int, high: int) -> Callable[[int], int]:
    def _range(x):
        if not (low <= int(x) < high):
            raise ValueError(f"{x} is not within range [{low}, {high})")
        return int(x)

    return _range


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="crossword-tex-gen", description="Generate Latex Wordsearches"
    )
    parser.add_argument("--width", type=_arg_int_range(1, 21))
    parser.add_argument("--height", type=_arg_int_range(1, 31))
    parser.add_argument('wordlist', type=argparse.FileType('rt'))
    args = parser.parse_args()

    wordlist = [w.strip().upper() for w in args.wordlist.readlines()]

    grid = generate_grid(args.width, args.height, wordlist)

    print(grid_to_tex(grid))
