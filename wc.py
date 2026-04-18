"""
Word Count (wc) Clone
=====================

This module provides a command-line utility to count lines, words, characters, bytes, and maximum line lengths in files, mimicking the Unix 'wc' command.

Usage:
    py wc.py [option ...] [file ...]
    py wc.py [option ...] --files0-from=F

:license: MIT, see LICENSE for more details.
"""
import argparse
import sys
from dataclasses import dataclass


@dataclass
class Stats:
    """
    A data container for file metrics.

    :param name: Path or name of the file being measured.
    :type name: str
    :param lines: Total number of lines.
    :type lines: int
    :param words: Total number of words separated by whitespace.
    :type words: int
    :param chars: Total number of characters.
    :type chars: int
    :param bytes: Total size of the file in bytes.
    :type bytes: int
    :param max_line_length: Maximum display width of a line (Tab is expanded to 8 characters).
    :type max_line_length: int
    """
    name: str
    lines: int = 0
    words: int = 0
    chars: int = 0
    bytes: int = 0
    max_line_length: int = 0


def display_data(data: list[Stats]) -> None:
    """
    Format and print the calculated statistics to the console.

    Calculates the total for each metric if multiple files were processed
    and aligns the output for readability.

    :param data: A list of Stats objects, each representing a file's statistics.
    :type data: list[Stats]
    :return: None
    """
    pass


def process_files(options: argparse.Namespace) -> None:
    """
    Coordinate the processing of input files based on provided flags.

    :param options: A namespace object containing CLI arguments
    :type options: argparse.Namespace
    :return: None
    """
    all_stats: list[Stats] = []

    for file_name in options.files:
        file_stats: Stats = Stats(name=file_name)

        try:
            with open(file_name) as file:
                for line in file.readlines():
                    file_stats.lines += 1
                    file_stats.words += len(line.split())
                    file_stats.chars += len(line)
                    file_stats.bytes += len(line.encode())
                    # Tabs are expanded because the Unix wc tool counts the display length of the lines
                    file_stats.max_line_length = max(
                        file_stats.max_line_length, len(line.expandtabs())
                    )
        except Exception as e:
            print(f"wc: {file_name}: {e}", file=sys.stderr)
            sys.exit(1)

        all_stats.append(file_stats)

    total_stats: Stats = Stats(
        name="total",
        lines=sum(stats.lines for stats in all_stats),
        words=sum(stats.words for stats in all_stats),
        chars=sum(stats.chars for stats in all_stats),
        bytes=sum(stats.bytes for stats in all_stats),
        max_line_length=max(stats.max_line_length for stats in all_stats)
    )
    all_stats.append(total_stats)

    display_data(all_stats)


def main() -> None:
    """
    Executes the command-line interface for the wc tool.

    This function parses command-line arguments using :mod:`argparse`, 
    initializes the file processing workflow, and outputs the results 
    to the standard output.

    :return: None
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="""A Python clone of the Unix wc utility.
This tool counts the number of lines, words, bytes,
and characters in the specified files.""",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # --- Options ---
    parser.add_argument(
        "-l",
        "--lines",
        action="store_true",
        help="Print the newline count(s)"
    )
    parser.add_argument(
        "-w",
        "--words",
        action="store_true",
        help="Print the word count(s)"
    )
    parser.add_argument(
        "-m",
        "--chars",
        action="store_true",
        help="Print the character count(s)"
    )
    parser.add_argument(
        "-c",
        "--bytes",
        action="store_true",
        help="Print the bytes count(s)"
    )
    parser.add_argument(
        "-L",
        "--max-line-length",
        action="store_true",
        help="Print the maximum display width"
    )
    parser.add_argument(
        "--total",
        choices=["always", "only", "never"],
        metavar="WHEN",
        help="""Print a total line when outputting more than one file.
WHEN can be:
    'always' - always print a total
    'only' - only print the total
    'never' - never print the total""",
        default="always"
    )
    parser.add_argument(
        "--files0-from",
        type=str,
        metavar="F",
        help="""Read input from the files specified by NUL-terminated names in file F.
If F is \"-\" then read names from standard input."""
    )

    parser.add_argument(
        "files",
        nargs="*",
        default=["sys.stdin"],
        help="Input file(s) to process. If no files are specified, or if \"-\" is provided, read from standard input."
    )

    args: argparse.Namespace = parser.parse_args()

    if args.files0_from:
        file_path: str | int = args.files0_from
        if file_path == "-":
            file_path = 0  # File descriptor for sys.stdin
    
        try:
            with open(file_path, "rb") as files0_from:
                file_names: list[str] = [
                    file_name.decode("utf-8", "replace")
                    for file_name in files0_from.read().split(b"\0")  # Split on 0 byte (ASCII NUL)
                    if file_name  # Filter out trailing empty strings
                ]
        except Exception as e:
            print(f"wc: {file_path if file_path != "-" else "standard input"}: {e}", file=sys.stderr)
            sys.exit(1)

        args.files = file_names

    print(args)
    process_files(args)
    

if __name__ == "__main__":
    main()
