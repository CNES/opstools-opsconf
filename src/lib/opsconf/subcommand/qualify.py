import logging
import os

import opsconf
import opsconf.libgit as libgit

LOGGER = logging.getLogger('opsconf.qualify')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Set the version VERSION of the file FILE as 'in qualification'."
    parentParser.add_argument('file', metavar='FILE', help="the file to qualify")
    parentParser.add_argument('version', metavar='VERSION', help="the version to qualify (last by default)", nargs='?')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    if args.version is None:
        lastCommitMsg = libgit.logLastOneFile(filename, opsconf.OPSCONF_BRANCH_WORK,
                                              pattern=opsconf.OPSCONF_PREFIX_PATTERN,
                                              outputFormat="%s")
        version = opsconf.getVersionFromCommitMsg(lastCommitMsg)
    else:
        version = opsconf.versionToInt(args.version)

    if opsconf.isCurrentBranchWork():
        _caseBranchIsWork(opsconf.OPSCONF_BRANCH_QUALIF, filename, version)
    elif opsconf.isCurrentBranchQualif():
        opsconf.retrieveVersion(opsconf.OPSCONF_BRANCH_WORK, filename, version)
    else:
        raise opsconf.OpsconfFatalError("Qualifying a file can only be done on the '{}' branch. Aborting.".format(opsconf.OPSCONF_BRANCH_QUALIF))


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
