"""Module to define the subcommand liststates."""

def setupParser(parser):
    """Setup the parser with the details of the current operation

    Args:
        parser (argparse.ArgumentParser): the parser to setup
    """
    parser.description = "NOT IMPLEMENTED YET"
    

def runCmd(args):
    """Run the command of the current operation

    Args:
        args (argparse.Namespace): the namespace returned by the parse_args() method
    """
    print(args)
    raise NotImplementedError("NOT IMPLEMENTED YET")
