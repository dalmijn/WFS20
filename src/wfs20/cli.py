"""Command-line interface for WFS20."""
import argparse
import sys
from argparse import PARSER, Action, HelpFormatter, _MutuallyExclusiveGroup
from collections.abc import Iterable
from pathlib import Path

from wfs20.version import __version__


class MainHelpFormatter(HelpFormatter):
    """_summary_."""

    def add_usage(
        self,
        usage: str | None,
        actions: Iterable[Action],
        groups: Iterable[_MutuallyExclusiveGroup],
        prefix: str | None = None,
    ) -> None:
        """_summary_."""
        return super().add_usage(usage, actions, groups, prefix)

    def _format_action(self, action):
        parts = super()._format_action(action)
        if action.nargs == PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts

    def start_section(self, heading):
        """_summary_."""
        heading = heading[0].upper() + heading[1:]
        return super().start_section(heading)


def file_path_check(path):
    """Cli friendly version of path checking."""
    root = Path.cwd()
    path = Path(path)
    if not path.is_absolute():
        path = Path(root, path)
    if not (path.is_file() | path.is_dir()):
        raise FileNotFoundError(f"{str(path)} is not a valid path")
    return path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        #    usage="%(prog)s <options> <commands>",
        add_help=False,
        formatter_class=MainHelpFormatter,
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"WFS20 v{__version__}",
        help="Show the version number",
    )

    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])
    args.func(args)


if __name__ == "__main__":
    main()
