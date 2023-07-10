import opsconf


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Show the versions of the files of the current state of the repo, or given branch BRANCH or tag TAG"
    parentParser.add_argument('revision', metavar='BRANCH|TAG', help="change to given branch or tag", nargs='?', default="HEAD")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    revision = args.revision
    fileVersionList = opsconf.showCurrentVersions(revision)

    maxlength = max([ len(fileVersion['file']) for fileVersion in fileVersionList ])
    for fileVersion in fileVersionList:

        if fileVersion['removed']:
            versionString = "v{}{}".format(fileVersion['version'], opsconf.OPSCONF_SYMBOL_REMOVED)
        elif fileVersion['newer']:
            versionString = "v{}{}".format(fileVersion['version'], opsconf.OPSCONF_SYMBOL_NEWER)
        else:
            versionString = "v{}".format(fileVersion['version'])
        print('| {:{maxlength}} | {:6} |'.format(fileVersion['file'], versionString, maxlength=maxlength))
