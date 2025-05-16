# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand checkout."""

import logging

import opsconf
from opsconf import libgit

LOGGER = logging.getLogger('opsconf.checkout')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Change to given BRANCH or TAG"
    parser.add_argument('revision', metavar='BRANCH|TAG', help="the branch or tag to checkout")

    parser.epilog = "DEPRECATED: use 'opsconf switch' instead"


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    LOGGER.warning("DEPRECATED: deprecated command. Use 'opsconf switch' instead")

    revision = args.revision
    libgit.switchToRevision(revision)
    opsconf.sync(libgit.getCurrentBranch())
    LOGGER.info("You are now on branch %s", revision)
