"""Module to define the toolbox script qualifyFromFile."""

import argparse
import logging
import os
import re
import sys

import opsconf
from opsconf import libgit

LOGGER = logging.getLogger('opsconf.toolbox.validateFromFile')

# the pattern is the folloxing:
# | filename     | v2{symbols}  |
INPUT_PATTERN = re.compile(r"^\|\s+(.+)\s*\|\s+v(\d+).*\s*\|$")


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Validate file versions based on the the stdin or the SRCFILE description."
    parentParser.add_argument('--dry-run', help="pretend to validate the files, but do not do it", action='store_true')
    parentParser.add_argument('sourceFilename', help="the file that lists the versions to validate, defaults to the stdin",
                              metavar='SRCFILE', nargs='?', type=argparse.FileType('r'), default=sys.stdin)


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    sourceFilename = args.sourceFilename

    if libgit.getCurrentBranch() not in [opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_VALID]:
        raise opsconf.OpsconfFatalError("Validating a file can only be done on branch '{}' or '{}'. Aborting."
                                        .format(opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_VALID))

    fileVersionList = []
    for lineno, line in enumerate(sourceFilename):
        line = line.rstrip()
        # the result of the match is [ ( 'filename', version ) ]
        matchResult = INPUT_PATTERN.findall(line)
        if len(matchResult) == 1:
            filename, version = matchResult[0]
            filename = filename.rstrip()
            version = int(version)
            fileVersionList.append((filename,version))
        else:
            raise opsconf.OpsconfFatalError("Error in file {}, line {}. Could not understand the file/version pair."
                                            .format(sourceFilename, lineno + 1))

    if args.dry_run:
        errorNb = 0
        for filename, version in fileVersionList:
            allVersionsFromFile = opsconf.listAllVersions(filename)
            if len(allVersionsFromFile) == 0:
                logging.error("Dry-run: Would fail: %s not found in %s.", filename, opsconf.OPSCONF_BRANCH_WORK)
                errorNb +=1
            elif allVersionsFromFile[0]['version'] < version:
                logging.error("Dry-run: Would fail: %s, v%d not found in %s (max version=v%d).",
                              filename, version, opsconf.OPSCONF_BRANCH_WORK, allVersionsFromFile[0]['version'])
                errorNb +=1
            else:
                logging.info("Dry-run: Would validate %s in v%d.", filename, version)
        if errorNb > 0:
            raise opsconf.OpsconfFatalError("Error where found. See above for details.")

    else:
        for filename, version in fileVersionList:
            opsconf.promoteVersion(opsconf.OPSCONF_BRANCH_VALID, filename, version)
            logging.info("Validated %s in v%d.", filename, version)
