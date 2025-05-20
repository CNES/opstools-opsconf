# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand move."""

from argparse import Namespace
import logging
import os
import shutil

import opsconf
import opsconf.subcommand.commit
import opsconf.subcommand.remove

LOGGER = logging.getLogger('opsconf.move')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Move file (or directory) SRC_FILE to DST_FILE with the justification MESSAGE"
    parser.add_argument('-m', metavar='REASON', help="the reason for the move", required=True, dest="reason")
    parser.add_argument('srcfile', metavar='SRC_FILE', help="the source path")
    parser.add_argument('dstfile', metavar='DST_FILE', help="the destination path")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    srcfile = args.srcfile
    dstfile = args.dstfile
    reason = args.reason

    if os.path.isdir(srcfile):
        shutil.copytree(srcfile, dstfile, symlinks=True)
    else:
        shutil.copy2(srcfile, dstfile, follow_symlinks=False)

    argsCommit = Namespace(file=dstfile, recursive=True, message=reason)
    argsRemove = Namespace(file=srcfile, recursive=True, reason=reason)
    opsconf.subcommand.commit.runCmd(argsCommit)
    opsconf.subcommand.remove.runCmd(argsRemove)
