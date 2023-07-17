import logging
import os

import opsconf
import opsconf.libgit as libgit

LOGGER = logging.getLogger('opsconf.validate')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Set the version VERSION of the file FILE as 'validated'."
    parser.add_argument('file', metavar='FILE', help="the file to validate")
    parser.add_argument('version', metavar='VERSION', help="the version to validate (last by default)", nargs='?')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    version = args.version

    if libgit.getCurrentBranch() not in [opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_VALID]:
        raise opsconf.OpsconfFatalError("Validating a file can only be done on branch '{}' or '{}'. Aborting.".format(opsconf.OPSCONF_BRANCH_WORK, opsconf.OPSCONF_BRANCH_VALID))

    opsconf.promoteVersion(opsconf.OPSCONF_BRANCH_VALID, filename, version)
