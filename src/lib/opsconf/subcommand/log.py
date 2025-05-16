# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand log."""

import csv
import logging
import sys

import opsconf
from opsconf import libgit

LOGGER = logging.getLogger('opsconf.log')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Check existing versions of file FILE in the current branch (or in all branches if \"--all\")"
    parser.add_argument('-a', '--all', help="check in all branches", action='store_true', dest='allVersions')
    parser.add_argument('--to-csv', help="output in csv", action='store_true', dest='toCsv')
    parser.add_argument('file', help="the file to apply the command to", metavar="FILE")

def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    allVersions = args.allVersions
    filename = args.file
    toCsv = args.toCsv

    if allVersions:
        branch = opsconf.OPSCONF_BRANCH_WORK
        versionListLastToFirst = opsconf.listAllVersions(filename)
    else:
        branch = libgit.getCurrentBranch()
        versionListLastToFirst = opsconf.listCurrentVersions(filename)

    # We want the versions from first to last
    versionList = reversed(versionListLastToFirst)

    LOGGER.info("On branch %s", branch)
    if toCsv:
        _csvPrint(versionList)
    else:
        _tablePrint(versionList)


def _csvPrint(versionList):
    """Internal function to print to the stdout as CSV.

    Args:
        versionList (list of dict): the list to print.
    """
    csvWriter = csv.writer(sys.stdout, dialect='excel', delimiter=";")

    fieldnames = ['version', 'subject', 'tags']
    csvWriter.writerow(fieldnames)

    for version in versionList:
        csvWriter.writerow([version['version'],
                            version['subject'],
                            ' '.join(version['tags'])])


def _tablePrint(versionList):
    """Internal function to print to the stdout as a table.

    Args:
        versionList (list of dict): the list to print.
    """
    rowTemplate = '| {:5} | {:40} | {:20} |'
    if sys.stdout.isatty():
        print(rowTemplate.format('vers.','subject', 'tags'))
        print(rowTemplate.format('-'*5, '-'*40, '-'*20))
    for version in versionList:
        print(rowTemplate.format(version['version'],
                                 version['subject'],
                                 ' '.join(version['tags'])))
