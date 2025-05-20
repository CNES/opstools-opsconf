# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand remove."""

import logging
import os

import opsconf

LOGGER = logging.getLogger('opsconf.remove')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Remove file FILE or the files contained in the directory DIRECTORY with the justification REASON"
    parser.add_argument('-m', metavar='REASON', help="the reason for removal", required=True, dest="reason")
    parser.add_argument('-r', help="remove recursively", action='store_true', dest="recursive")
    parser.add_argument('file', metavar='FILE', help="the file to remove (or directory if option '-r' is used)")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    reason = args.reason
    recursive = args.recursive

    if os.path.islink(filename) or os.path.isfile(filename):
        answer = input("Are you sure you want to remove this file (y,N)\n> {}\n".format(filename))
        if answer.lower() not in ['y', 'yes']:
            LOGGER.info("Aborted: nothing was done")
            return
        opsconf.removeFile(filename, reason)
        LOGGER.info("File removed: \"%s\"", filename)


    elif os.path.isdir(filename):
        if not recursive:
            raise opsconf.OpsconfFatalError("Directory removal must be recursive. Use the '-r' option.")

        answer = input("Are you sure you want to remove this folder and *all* its content? (y,N)\n> {}\n".format(filename))
        if answer.lower() not in ['y', 'yes']:
            LOGGER.info("Aborted: nothing was done")
            return
        for root, _, files in os.walk(filename, topdown=False):
            for name in files:
                subfilename = os.path.join(root, name)
                opsconf.removeFile(subfilename, reason)
                LOGGER.info("File removed: \"%s\"", subfilename)

    else:
        raise opsconf.OpsconfFatalError("I don't know what to do with this file: {}".format(filename))
