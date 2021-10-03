#!/usr/bin/env python3

import logging
import sys

from arguments import CLI

from login import Login
from export import Export
from import_workouts import Import

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def main():
    cli = CLI()
    args = cli.init_parser()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.help:
        cli.print_help()
        exit(0)

    if args.command == 'login':
        login = Login(args)
    elif args.command == 'logout':
        login = Login()
        login.logout()
    else:
        login = Login(args)
        session = login.get_session()
        if args.command == 'export':
            Export(args, session)
        elif args.command == 'import':
            Import(args, session)
        else:
            cli.print_help()


if __name__ == "__main__":
    main()
