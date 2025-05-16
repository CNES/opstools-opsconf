# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand tag."""

import time

from opsconf import libgit


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Tag the current state of the repository with tag TAG"
    parser.add_argument('-m', help="the tag message", metavar="MESSAGE", dest="message")
    parser.add_argument('tag', help="the name of the tag", metavar='TAG')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    tag = args.tag
    if args.message is None:
        message = "tag: {} ({})".format(tag, time.strftime('%d/%m/%Y %H:%M:%S'))
    else:
        message = args.message
    libgit.setTag(tag, message)
    libgit.pushTag(tag)
