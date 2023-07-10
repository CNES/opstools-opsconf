import opsconf
import opsconf.libgit as libgit


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Synchronize the local and distant repositories"
    parentParser.add_argument('remote', help="change to given branch or tag", metavar='REMOTE', nargs='?', default='origin')


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    remote = args.remote
    currentBranch = libgit.getCurrentBranch()
    
    opsconf.sync(currentBranch, remote)
