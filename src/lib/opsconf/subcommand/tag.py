"""Module to define the subcommand tag."""

from opsconf import libgit


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Tag the current state of the repository with tag TAG"
    parser.add_argument('tag', help="the name of the tag", metavar='TAG')

   
def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    tag = args.tag
    libgit.setTag(tag)
    libgit.pushTag(tag)
