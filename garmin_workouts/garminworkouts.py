#!/usr/bin/env python3

import logging
import sys

from arguments import CLI

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    cli = CLI()
    cli.init_parser()


if __name__ == "__main__":
    main()
