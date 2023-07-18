"""Module to define the subcommand status."""

import opsconf


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Show the versions of the files of the current state of the repo, or given branch BRANCH or tag TAG"
    parser.add_argument('--withNotes', help="whether to get the qualification/validation notes or not", action='store_true')
    parser.add_argument('revision', metavar='BRANCH|TAG', help="change to given branch or tag", nargs='?', default="HEAD")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    revision = args.revision
    withNotes = args.withNotes

    fileVersionList = opsconf.showCurrentVersions(revision, withNotes=withNotes)

    maxlength = max([ len(fileVersion['file']) for fileVersion in fileVersionList ])
    for fileVersion in fileVersionList:

        if fileVersion['removed']:
            versionString = "v{}{}".format(fileVersion['version'], opsconf.OPSCONF_SYMBOL_REMOVED)
        elif fileVersion['newer']:
            versionString = "v{}{}".format(fileVersion['version'], opsconf.OPSCONF_SYMBOL_NEWER)
        else:
            versionString = "v{}".format(fileVersion['version'])

        if fileVersion['changed']:
            versionString += opsconf.OPSCONF_SYMBOL_CHANGED

        if withNotes:
            print('| {:{maxlength}} | {:6} | {:40} |'.format(fileVersion['file'], versionString, '/'.join(fileVersion['notes']),
                                                           maxlength=maxlength))
        else:
            print('| {:{maxlength}} | {:6} |'.format(fileVersion['file'], versionString, maxlength=maxlength))
