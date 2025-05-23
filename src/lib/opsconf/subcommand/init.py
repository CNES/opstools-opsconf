# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Module to define the subcommand init."""

import logging
import os
import shutil
import stat

import opsconf
from opsconf import libgit

HOOK_SRC = opsconf.OPSCONF_HOOKDIR

LOGGER = logging.getLogger('opsconf.init')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Initialize (or re-iniialize the repository)."
    parser.add_argument('--root-branch', help="the branch used to initialize '{}' branch with".format(opsconf.OPSCONF_BRANCH_WORK),
                        metavar='BRANCH')


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
            raise opsconf.OpsconfFatalError("This repo is not made for opsconf. To allow migration, use the '--root-branch BRANCH' option")
        LOGGER.info("Porting standard git repository to opsconf")
        opsconf.initBranches(rootBranch)

    LOGGER.info("Force using hooks in .git/hooks")
    libgit.setConfig('core.hooksPath', '.git/hooks')

    LOGGER.info("Updating hooks")
    hookDestination = os.path.join(gitRoot, ".git/hooks")
    for hook in os.listdir(HOOK_SRC):
        destinationFile = os.path.join(hookDestination, hook)
        if os.path.isfile(destinationFile):
            os.remove(destinationFile)
        shutil.copy(os.path.join(HOOK_SRC, hook), destinationFile)
        statInfo = os.stat(destinationFile)
        os.chmod(destinationFile, statInfo.st_mode | stat.S_IXUSR | stat.S_IXGRP)
    LOGGER.info("Hooks updated")
