import logging

import opsconf

LOGGER = logging.getLogger('opsconf.remove')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Remove file FILE with the justification REASON"
    parentParser.add_argument('-m', metavar='REASON', help="the reason for removal", required=True, dest="reason")
    parentParser.add_argument('file', metavar='FILE', help="the file to remove")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    filename = args.file
    reason = args.reason

    answer = input("Are you sure you want to remove this file (y,N)\n> {}\n".format(filename))
    if answer.lower() in ['y', 'yes']:
        opsconf.removeFile(filename, reason)
    else:
        LOGGER.info("Aborting...")
