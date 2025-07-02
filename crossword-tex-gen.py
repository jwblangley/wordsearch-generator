width = 5
height = 3


def grid_to_tex(grid: list[list[str]]) -> str:
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


if __name__ == "__main__":
    grid = [["A"] * width] * height

    print(grid_to_tex(grid))
