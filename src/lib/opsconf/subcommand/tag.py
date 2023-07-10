import opsconf.libgit as libgit


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Tag the current state of the repository with tag TAG"
    parentParser.add_argument('tag', help="the name of the tag", metavar='TAG')

   
def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    tag = args.tag
    libgit.setTag(tag)
    libgit.pushTag(tag)
