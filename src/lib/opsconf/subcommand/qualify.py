# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand qualify."""

import logging
import os

import opsconf
from opsconf import libgit

LOGGER = logging.getLogger('opsconf.qualify')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Set the version VERSION of the file FILE as 'in qualification'."
    parser.add_argument('-m', help="an optional reason for the validation",
                        metavar='MESSAGE', dest='message')
    parser.add_argument('file', help="the file to qualify", metavar='FILE')
    parser.add_argument('version', help="the version to qualify (last by default)",
                        metavar='VERSION', nargs='?')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    version = opsconf.versionToInt(args.version)
    message = args.message

    if libgit.getCurrentBranch() not in [opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_QUALIF]:
        raise opsconf.OpsconfFatalError("Qualifying a file can only be done on branch '{}' or '{}'. Aborting."
                                        .format(opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_VALID)
                                       )

    opsconf.promoteVersion(opsconf.OPSCONF_BRANCH_QUALIF, filename, version, message)
