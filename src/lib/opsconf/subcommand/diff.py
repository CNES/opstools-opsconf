import opsconf


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Show the différence of FILE between version VERSION_OLD and VERSION_NEW"
    parser.add_argument('file', metavar='FILE', help="the file on which to do the diff")
    parser.add_argument('version_old', metavar='VERSION_OLD', help="the old version to compare to")
    parser.add_argument('version_new', metavar='VERSION_NEW', help="the new version to compare to (default HEAD)", nargs='?', default="HEAD")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    v1 = args.version_old
    v2 = args.version_new
    opsconf.diffBetweenVersions(filename, v1, v2)
