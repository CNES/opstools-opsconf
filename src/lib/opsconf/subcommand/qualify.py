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
    parser.add_argument('file', metavar='FILE', help="the file to qualify")
    parser.add_argument('version', metavar='VERSION', help="the version to qualify (last by default)", nargs='?')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    version = args.version

    if libgit.getCurrentBranch() not in [opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_QUALIF]:
        raise opsconf.OpsconfFatalError("Qualifying a file can only be done on branch '{}' or '{}'. Aborting."
                                        .format(opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_VALID)
                                       )

    opsconf.promoteVersion(opsconf.OPSCONF_BRANCH_QUALIF, filename, version)
