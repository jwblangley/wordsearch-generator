import argparse
import random

from typing import Callable

letter_frequencies = {
    "a": 0.08167,
    "b": 0.01492,
    "c": 0.02782,
    "d": 0.04253,
    "e": 0.12702,
    "f": 0.02228,
    "g": 0.02015,
    "h": 0.06094,
    "i": 0.06966,
    "j": 0.00153,
    "k": 0.00772,
    "l": 0.04025,
    "m": 0.02406,
    "n": 0.06749,
    "o": 0.07507,
    "p": 0.01929,
    "q": 0.00095,
    "r": 0.05987,
    "s": 0.06327,
    "t": 0.09056,
    "u": 0.02758,
    "v": 0.00978,
    "w": 0.02360,
    "x": 0.00150,
    "y": 0.01974,
    "z": 0.00074,
}


def grid_to_tex(
    grid: list[list[str]], answer_key: list[list[str]], included_words: list[str]
) -> str:
    return (
        r"""
\documentclass[12pt]{article}

\usepackage[a4paper, margin=2cm]{geometry}
\usepackage[table]{xcolor}
\usepackage{multicol}
\usepackage{easytable}
\usepackage{xcolor}

\pagenumbering{gobble}

\renewcommand{\familydefault}{\sfdefault}

\newlength{\cellsize}
\setlength{\cellsize}{0.75cm}

\begin{document}

\noindent
\begin{center}
    \begin{TAB}(e,\cellsize,\cellsize){|"""
        + r"c" * len(grid[0])
        + r"|}"
        + r"{|"
        + r"c" * len(grid)
        + "|}\n"
        + "\n".join(("    " + " & ".join(ls) + " \\\\") for ls in grid)
        + r"""
    \end{TAB}
\end{center}

\vspace{2cm}

\begin{multicols}{3}
    \noindent
"""
        + "\n".join(f"    {w}\\\\" for w in sorted(included_words))
        + r"""
\end{multicols}

\pagebreak

\begin{center}
    \begin{TAB}(e,\cellsize,\cellsize){|"""
        + r"c" * len(grid[0])
        + r"|}"
        + r"{|"
        + r"c" * len(grid)
        + "|}\n"
        + "\n".join(
            (
                "    "
                + " & ".join(
                    (
                        (
                            f"\colorbox{{yellow!50}}{{{l}}} "
                            if answer_key[y][x] != " "
                            else l
                        )
                    )
                    for x, l in enumerate(ls)
                )
                + " \\\\"
            )
            for y, ls in enumerate(grid)
        )
        + r"""
    \end{TAB}
\end{center}

\end{document}
"""
    )


def generate_grid(
    width: int,
    height: int,
    wordlist: list[str],
    target_fill_rate: float = 0.4,
    give_up_rate: float = 0.0001,
) -> tuple[list[list[str]], list[list[str]], list[str]]:
    grid = [[" " for _ in range(width)] for _ in range(height)]
    max_word_len = max(width, height)

    # Start with largest_words - easier to fit earlier
    wordlist = list(
        sorted(
            (w for w in wordlist if len(w) <= max_word_len),
            key=(lambda w: len(w)),
            reverse=True,
        )
    )

    # Randomly select words
    mean_word_len = sum(len(w) for w in wordlist) / len(wordlist)
    mean_num_fit = (width * height) / mean_word_len
    heuristic_rate = target_fill_rate * (mean_num_fit / len(wordlist))

    # Start at 1 to keep maths valid: skew is negligble for large numbers
    attempts = 1
    successes = 1

    successful_words = list()

    word_iter = iter(w for w in wordlist if random.random() < heuristic_rate)

    word_to_fit = next(word_iter, None)
    if word_to_fit is None:
        word_to_fit = wordlist[0]

    while successes <= 1 or (
        successes / attempts > give_up_rate and word_to_fit is not None
    ):
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
            successful_words.append(word_to_fit)
            word_to_fit = next(word_iter, None)

    answer_key = [[grid[y][x] for x in range(width)] for y in range(height)]

    for y in range(height):
        for x in range(width):
            if grid[y][x] == " ":
                grid[y][x] = random.choices(
                    list(k.upper() for k in letter_frequencies.keys()),
                    letter_frequencies.values(),
                )[0]

    return grid, answer_key, successful_words


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
    parser.add_argument("wordlist", type=argparse.FileType("rt"))
    args = parser.parse_args()

    wordlist = [
        "".join(ch for ch in w.strip().upper() if ch.isalpha())
        for w in args.wordlist.readlines()
    ]
    wordlist = [w for w in wordlist if w != ""]

    print(grid_to_tex(*generate_grid(args.width, args.height, wordlist)))
