"""Module to define the subcommand toolbox. Since we don't know the scripts from the toolbox,
we need to do clever things to discover them on the run."""

import glob
import logging
import os

import opsconf

modules = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
__all__ = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]

# the import shall be here so that __all__ is already defined
# pylint: disable=wrong-import-position, import-self
from . import *


LOGGER = logging.getLogger('opsconf.toolbox')

def setupParser(parser):
    """Setup the parser with the details of the current operation.

    Args:
        parser (argparse.ArgumentParser): the parser to setup.
    """
    parser.description = "Toolbox scripts on top of opsconf"


def runCmd(args):
    """Run the command of the current operation.

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method.
    """
    if args.script in __all__:
        # No better solution than an eval(). If you have a better idea, MR welcome
        # pylint: disable=eval-used
        eval(args.script).runCmd(args)


def setupSubParsers(parser, parentParser):
    """Setup the subparsers of the toolbox entry.

    Args:
        parser (argparse.ArgumentParser): the parser on which to setup the subparsers.
        parentParser (argparse.ArgumentParser): the parser which holds the common arguments.
    """
    subparserDict = {}
    subparsers = parser.add_subparsers(title='Opsconf Toolbox', dest='script')
    for script in __all__:
        parser = subparsers.add_parser(script, parents=[parentParser])
        # No better solution than an eval(). If you have a better idea, MR welcome
        # pylint: disable=eval-used
        eval(script).setupParser(parser)
        subparserDict[script] = parser
