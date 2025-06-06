# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the toolbox script qualifyFromFile."""

import argparse
import csv
import logging
import sys

import opsconf
from opsconf import libgit

LOGGER = logging.getLogger('opsconf.toolbox.qualifyFromFile')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Qualify file versions based on the the stdin or the SRCFILE description."
    parentParser.add_argument('--dry-run', help="pretend to qualify the files, but do not do it", action='store_true')
    parentParser.add_argument('-m', help="optional reason for the qualification", metavar='MESSAGE', dest='message')
    parentParser.add_argument('sourceFile', help="the file that lists the versions to qualify (in csv), defaults to the stdin",
                              metavar='SRCFILE', nargs='?', type=argparse.FileType('r'), default=sys.stdin)


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    sourceFile = args.sourceFile
    message = args.message

    if libgit.getCurrentBranch() not in [opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_QUALIF]:
        raise opsconf.OpsconfFatalError("Qualifying a file can only be done on branch '{}' or '{}'. Aborting."
                                        .format(opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_QUALIF))

    fileVersionList = csv.DictReader(sourceFile, delimiter=';', dialect='excel')

    if args.dry_run:
        errorNb = 0
        for fileVersion in fileVersionList:
            filename = fileVersion['filename']
            version = int(fileVersion['version'])
            allVersionsFromFile = opsconf.listAllVersions(filename)
            if len(allVersionsFromFile) == 0:
                logging.error("Dry-run: Would fail: %s not found in %s.", filename, opsconf.OPSCONF_BRANCH_WORK)
                errorNb +=1
            elif allVersionsFromFile[0]['version'] < version:
                logging.error("Dry-run: Would fail: %s, v%d not found in %s (max version=v%d).",
                              filename, version, opsconf.OPSCONF_BRANCH_WORK, allVersionsFromFile[0]['version'])
                errorNb +=1
            else:
                logging.info("Dry-run: Would qualify %s in v%d.", filename, version)
        if errorNb > 0:
            raise opsconf.OpsconfFatalError("Error where found. See above for details.")

    else:
        for fileVersion in fileVersionList:
            filename = fileVersion['filename']
            version = int(fileVersion['version'])
            opsconf.promoteVersion(opsconf.OPSCONF_BRANCH_QUALIF, filename, version, message)
            logging.info("Validated %s in v%d.", filename, version)
