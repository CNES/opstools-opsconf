# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

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
