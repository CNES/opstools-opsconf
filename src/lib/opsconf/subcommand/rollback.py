import opsconf


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Create a new version of FILE with previous version VERSION, with the justification REASON"
    parentParser.add_argument('-m', metavar='REASON', help="the reason for rolling-back", required=True, dest="reason")
    parentParser.add_argument('file', metavar='FILE', help="the file to rollback")
    parentParser.add_argument('version', metavar='VERSION', help="the version to rollback")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    version = opsconf.versionToInt(args.version)
    reason = args.reason

    opsconf.checkBranchIsWork()
    opsconf.checkBranchUpToDate()
    opsconf.rollbackToVersion(filename, version, reason)
