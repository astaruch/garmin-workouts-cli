#!/usr/bin/env python3

import logging
import sys

from arguments import CLI

from create import Create
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
        login.login()
    elif args.command == 'logout':
        login = Login()
        login.logout()
    elif args.command == 'export':
        export = Export(args)
        export.export()
    elif args.command == 'import':
        import_workouts = Import(args)
        import_workouts.import_workouts()
    elif args.command == 'create':
        Create(args)
    else:
        cli.print_help()


if __name__ == "__main__":
    main()
