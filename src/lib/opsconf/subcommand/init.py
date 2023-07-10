import logging
import os
import shutil
import stat

import opsconf
import opsconf.libgit as libgit

HOOK_SRC = opsconf.OPSCONF_HOOKDIR

LOGGER = logging.getLogger('opsconf.init')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Initialize (or re-iniialize the repository)."
    parentParser.add_argument('--root-branch', metavar='BRANCH', help="the branch used to initialize '{}' branch with".format(opsconf.OPSCONF_BRANCH_WORK))


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    rootBranch = args.root_branch

    if not libgit.isGitRepository():
        libgit.initRepository()
        LOGGER.info("Git repository initialized: %s", os.getcwd())
    else:
        LOGGER.info("I am already in a git repository, moving forwards")

    gitRoot = libgit.getGitRoot()
    if libgit.isRepositoryEmpty():
        LOGGER.info("Repository is empty, creating branches and first Readme")
        opsconf.initBranches()
    elif not opsconf.isOpsConfRepo():
        if rootBranch is None:
            raise opsconf.OpsconfFatalError("This repo is not made for opsconf. To allow migration, use the '--rot-branch BRANCH' option")
        LOGGER.info("Porting standard git repository to opsconf")
        opsconf.initBranches(rootBranch)
        
    LOGGER.info("Force using hooks in .git/hooks")
    libgit.setConfig('core.hooksPath', '.git/hooks')
    
    LOGGER.info("Updating hooks")
    hookDestination = os.path.join(gitRoot, ".git/hooks")
    for hook in os.listdir(HOOK_SRC):
        destinationFile = os.path.join(hookDestination, hook)
        shutil.copy(os.path.join(HOOK_SRC, hook), destinationFile)
        statInfo = os.stat(destinationFile)
        os.chmod(destinationFile, statInfo.st_mode | stat.S_IXUSR | stat.S_IXGRP)
    LOGGER.info("Hooks updated")
