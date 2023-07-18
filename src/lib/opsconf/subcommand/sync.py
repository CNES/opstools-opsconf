"""Module to define the subcommand sync."""

import opsconf
from opsconf import libgit


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Synchronize the local and distant repositories"
    parser.add_argument('remote', help="change to given branch or tag", metavar='REMOTE', nargs='?', default='origin')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    remote = args.remote
    currentBranch = libgit.getCurrentBranch()

    opsconf.sync(currentBranch, remote)
