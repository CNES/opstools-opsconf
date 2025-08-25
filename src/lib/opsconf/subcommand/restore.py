# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand rollback."""

import opsconf


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Restore the file content to the given version. The current content is saved to '<FILE>.restored'."
    parser.add_argument('file', metavar='FILE', help="the file to restore")
    parser.add_argument('version', help="the version to restore (last by default)",
                        metavar='VERSION', nargs='?')



def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    version = opsconf.versionToInt(args.version)

    opsconf.restoreFile(filename, version)
