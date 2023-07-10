import logging
import os

import opsconf
import opsconf.libgit as libgit

LOGGER = logging.getLogger('opsconf.validate')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Set the version VERSION of the file FILE as 'validated'."
    parentParser.add_argument('file', metavar='FILE', help="the file to validate")
    parentParser.add_argument('version', metavar='VERSION', help="the version to validate")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    version = opsconf.versionToInt(args.version)
    filename = args.file
    if opsconf.isCurrentBranchWork():
        _caseBranchIsWork(opsconf.OPSCONF_BRANCH_VALID, filename, version)
    elif opsconf.isCurrentBranchValid():
        opsconf.retrieveVersion(opsconf.OPSCONF_BRANCH_WORK, filename, version)
    else:
        raise opsconf.OpsconfFatalError("Validating a file can only be done on the '{}' branch. Aborting.".format(opsconf.OPSCONF_BRANCH_VALID))


def _caseBranchIsWork(targetBranch, filename, version):
    currentPath = os.getcwd()
    currentBranch = opsconf.OPSCONF_BRANCH_WORK

    LOGGER.debug("We are in branch %s", currentBranch)
    filePath = os.path.join(currentPath, filename)
    gitRootDir = libgit.getGitRoot()

    if filePath.startswith(gitRootDir):
        filePath.replace(gitRootDir, '', 1)

    try:
        os.chdir(gitRootDir)
        libgit.checkoutRevision(targetBranch)
        LOGGER.debug("We changed to branch %s", targetBranch)
        opsconf.retrieveVersion(opsconf.OPSCONF_BRANCH_WORK, filename, version)
    finally:
        libgit.checkoutRevision(currentBranch)
        LOGGER.debug("We are back in branch %s", currentBranch)
        os.chdir(currentPath)
