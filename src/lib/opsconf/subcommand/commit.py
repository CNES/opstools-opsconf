import logging
import os

import opsconf
import opsconf.libgit as libgit

LOGGER = logging.getLogger('opsconf.commit')


def setupParser(parentParser):
    """Setup the parser with the details of the current operation

    Args:
        parentParser (argparse.ArgumentParser): the parser to setup
    """
    parentParser.description = "Commit the single file FILE or the files contained in the directory DIRECTORY with the commit message MESSAGE"

    parentParser.add_argument('-m', help="the commit message", metavar="MESSAGE", dest="message")
    parentParser.add_argument('-r', help="commit recursively", action='store_true', dest="recursive")
    parentParser.add_argument("file", help="the file to commit (or directory if option '-r' is used", metavar="FILE|DIRECTORY")


def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    recursive = args.recursive
    message = args.message
    filename = args.file

    if not recursive and os.path.isdir(filename):
        raise RuntimeError("To commit a directory, use the option -r.")

    # Remove all added files: everything is done by the commit
    libgit.resetTree(mixed=True)

    if recursive and os.path.isdir(filename):
         # We search only changed file
         changedFiles = libgit.listChangedFiles()

         for f in changedFiles:
             _commitFile(f, message)
    else:
        _commitFile(filename, message=message)
    

def _commitFile(filename, message=None):
    """_summary_

    Args:
        filename (_type_): _description_
        message (_type_, optional): _description_. Defaults to None.

    Raises:
        RuntimeError: _description_
    """
    # we only know how to deal with files and links
    if not os.path.islink(filename) and not os.path.isfile(filename):
        raise opsconf.OpsconfFatalError("This is not a file or link: {}".format(filename))
    
    libgit.addOneFile(filename)
    LOGGER.debug("File added: \"%s\"", filename)
    libgit.commitOneFile(filename, message)

    commitMessage = libgit.logLastOneFile(filename, "HEAD",
                                          pattern=opsconf.OPSCONF_PREFIX_PATTERN,
                                          outputFormat="%s")
    version = opsconf.getVersionFromCommitMsg(commitMessage)

    LOGGER.info("File committed: \"%s\", v%d", filename, version)
