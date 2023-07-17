import logging

import opsconf

LOGGER = logging.getLogger('opsconf.remove')


def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "Remove file FILE with the justification REASON"
    parser.add_argument('-m', metavar='REASON', help="the reason for removal", required=True, dest="reason")
    parser.add_argument('file', metavar='FILE', help="the file to remove")


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
