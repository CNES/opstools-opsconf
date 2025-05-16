# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand status."""

import csv
import sys

import opsconf


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Show the versions of the files of the current state of the repo, or given branch BRANCH or tag TAG"
    parser.add_argument('--with-notes', help="whether to get the qualification/validation notes or not",
                        action='store_true', dest='withNotes')
    parser.add_argument('--to-csv', help="output in csv", action='store_true', dest='toCsv')
    parser.add_argument('revision', metavar='BRANCH|TAG', help="change to given branch or tag", nargs='?', default="HEAD")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    revision = args.revision
    withNotes = args.withNotes
    toCsv = args.toCsv

    fileVersionList = opsconf.showCurrentVersions(revision, withNotes=withNotes)


    if toCsv:
        _csvPrint(fileVersionList, withNotes)
    else:
        _tablePrint(fileVersionList, withNotes)


def _csvPrint(fileVersionList, withNotes):
    """Internal function to print to the stdout as CSV.

    Args:
        versionList (list of dict): the list to print.
        withNotes (bool): whether to print the notes or not.
    """
    csvWriter = csv.writer(sys.stdout, dialect='excel', delimiter=';')

    fieldnames = ['filename', 'version', 'removedInWork', 'newerVersionInWork', 'changed']
    if withNotes:
        fieldnames.append('notes')
    csvWriter.writerow(fieldnames)

    for fileVersion in fileVersionList:
        row = [
            fileVersion['file'],
            fileVersion['version'],
            fileVersion['removed'],
            fileVersion['newer'],
            fileVersion['changed']
        ]
        if withNotes:
            row.append('/'.join(fileVersion['notes']))
        csvWriter.writerow(row)


def _tablePrint(fileVersionList, withNotes):
    """Internal function to print to the stdout as a table.

    Args:
        versionList (list of dict): the list to print.
        withNotes (bool): whether to print the notes or not.
    """
    # define columns and print header
    rowTemplate = '| {:{maxlength}} | {:6} |'
    if len(fileVersionList) == 0:
        maxlength = 10
    else:
        maxlength = max([ len(fileVersion['file']) for fileVersion in fileVersionList ])

    if withNotes:
        rowTemplate += ' {:40} |'
        print(rowTemplate.format('Filename', 'Vers.', 'Notes', maxlength=maxlength))
        print(rowTemplate.format('-'*maxlength, '-'*6, '-'*40, maxlength=maxlength))
    else:
        print(rowTemplate.format('Filename', 'Vers.', maxlength=maxlength))
        print(rowTemplate.format('-'*maxlength, '-'*6, maxlength=maxlength))

    # print data
    for fileVersion in fileVersionList:
        if fileVersion['removed']:
            versionString = "v{}{}".format(fileVersion['version'], opsconf.OPSCONF_SYMBOL_REMOVED)
        elif fileVersion['newer']:
            versionString = "v{}{}".format(fileVersion['version'], opsconf.OPSCONF_SYMBOL_NEWER)
        else:
            versionString = "v{}".format(fileVersion['version'])

        if fileVersion['changed']:
            versionString += opsconf.OPSCONF_SYMBOL_CHANGED

        if withNotes:
            print(rowTemplate.format(fileVersion['file'], versionString,
                                     '/'.join(fileVersion['notes']), maxlength=maxlength))
        else:
            print(rowTemplate.format(fileVersion['file'], versionString, maxlength=maxlength))
