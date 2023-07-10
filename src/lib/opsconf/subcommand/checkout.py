import logging

import opsconf
import opsconf.libgit as libgit

LOGGER = logging.getLogger('opsconf.checkout')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Change to given BRANCH or TAG"
    parentParser.add_argument('revision', metavar='BRANCH|TAG', help="the branch or tag to checkout")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    revision = args.revision
    libgit.checkoutRevision(revision)
    opsconf.sync(libgit.getCurrentBranch())
    LOGGER.info("You are now on branch %s", revision)
