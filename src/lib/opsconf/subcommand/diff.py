"""Module to define the subcommand diff."""

import opsconf


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Show the différence of FILE between version VERSION_OLD and VERSION_NEW"
    parser.add_argument('file', help="the file on which to do the diff", metavar='FILE')
    parser.add_argument('version_old', help="the old version to compare to (defaults to the last version)",
                        metavar='VERSION_OLD', nargs='?', default=None)
    parser.add_argument('version_new', help="the new version to compare to (defaults to the state of the working directory)",
                        metavar='VERSION_NEW', nargs='?', default=None)


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    v1 = opsconf.versionToInt(args.version_old)
    v2 = opsconf.versionToInt(args.version_new)
    print(opsconf.diffBetweenVersions(filename, v1, v2))
