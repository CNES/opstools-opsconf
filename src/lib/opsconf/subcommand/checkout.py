# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand checkout."""

import logging

import opsconf
import opsconf.subcommand.switch
from opsconf import libgit

LOGGER = logging.getLogger('opsconf.checkout')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    opsconf.subcommand.switch.setupParser(parser)
    parser.epilog = "DEPRECATED: use 'opsconf switch' instead"


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    LOGGER.warning("DEPRECATED: deprecated command. Use 'opsconf switch' instead")

    opsconf.subcommand.switch.runCmd(args)
