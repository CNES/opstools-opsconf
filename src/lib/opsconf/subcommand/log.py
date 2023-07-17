import logging
import sys

import opsconf
import opsconf.libgit as libgit

LOGGER = logging.getLogger('opsconf.log')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Check existing versions of file FILE in the current branch (or in all branches if \"--all\")"
    parser.add_argument('file', help="the file to apply the command to", metavar="FILE")
    parser.add_argument('-a', '--all', help="check in all branches", action='store_true', dest='allVersions')

def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    allVersions = args.allVersions
    filename = args.file

    if allVersions:
        branch = opsconf.OPSCONF_BRANCH_WORK
        versionList = opsconf.listAllVersions(filename)
    else:
        branch = libgit.getCurrentBranch()
        versionList = opsconf.listCurrentVersions(filename)

    #if sys.stdout.isatty:
    #    print("On branch {}:".format(branch))
    LOGGER.info("On branch %s", branch)
    for version in versionList:
        print('| {:5} | {:40} | {:20} |'.format(version['version'],
                                                version['subject'],
                                                ' '.join(version['tags'])))
