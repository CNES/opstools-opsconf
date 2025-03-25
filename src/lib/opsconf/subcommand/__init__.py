"""Package containing all the subcommands that can be run by opsconf"""

from . import (
    # standard commands
    commit,
    diff,
    init,
    liststates,
    log,
    qualify,
    remove,
    rollback,
    status,
    switch,
    sync,
    tag,
    validate,
    # deprecated commands
    checkout,
    # other commands
    toolbox
    )
