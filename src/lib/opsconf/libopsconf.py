# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Library for opsconf functions. This module relies on opsconf.libgit."""
import logging
import os

from . import libgit

OPSCONFVERSION = "0.3.0"

OPSCONF_BRANCH_WORK = "work"
OPSCONF_BRANCH_QUALIF = "qualification"
OPSCONF_BRANCH_VALID = "master"

OPSCONF_PREFIX_PATTERN = "^v[0-9]\+: "
OPSCONF_PREFIX_REMOVED = "vZZ: "
OPSCONF_HOOKDIR = "{}/githooks".format(os.getenv('OPSCONF_DIR', '/usr/share/opsconf'))

OPSCONF_PROMOTION_NOTE_TOPIC = "promotion"

OPSCONF_SYMBOL_REMOVED = '!'
OPSCONF_SYMBOL_NEWER = '*'
OPSCONF_SYMBOL_CHANGED = '+'


LOGGER = logging.getLogger('opsconf')


class OpsconfFatalError(RuntimeError):
    """Error that shall stop the current process.
    """
    pass


def versionToInt(version):
    """Translate a version 'vXXX', 'XXX' or XXX to an integer XXX.

    For instance:
    >>> versionToInt('v12')
    12
    >>> versionToInt(12)
    12

    Args:
        version (int or string or None): The version to translate. If None, returns None

    Returns:
        int: the version as an integer
    """
    if version is None:
        return None
    elif isinstance(version, int):
        return version
    elif isinstance(version, str) and version.isdigit():
        return int(version)
    else:
        return int(version[1:])


def initBranches(rootBranch=None):
    """Initialize the branches that are needed for opsconf

    1) An orphan branch WORK is created.
    2) If a migration is needed (rootBranch given), all files from rootBranch are checked out
    and committed to this new branch. Otherwise, a README file is created.
    3) An '.opsconf' file is created
    4) The VALID and QUALIF branch are created (normally has orphan, but VALID might exist as an empty branch).
    5) They are initalized with the .opsconf file's creation commit.
    6) At the end, the repository is put on the WORK branch.

    Args:
        rootBranch (str, optional): the branch to migrate from. Defaults to None.

    Raises:
        OpsconfFatalError: if something goes wrong, this exception is raised.
    """
    if (libgit.existLocalBranch(OPSCONF_BRANCH_WORK) or
            libgit.existLocalBranch(OPSCONF_BRANCH_QUALIF) or
            libgit.existLocalBranch(OPSCONF_BRANCH_VALID)):
        raise OpsconfFatalError("One of the following branch exists, aborting: {}, {}, {}"
                                .format(OPSCONF_BRANCH_WORK, OPSCONF_BRANCH_QUALIF, OPSCONF_BRANCH_VALID)
                               )

    if os.path.isfile("{}/.opsconf".format(libgit.getGitRoot)):
        raise OpsconfFatalError(".opsconf file already exists. Aborting.")

    if rootBranch is not None:
        libgit.switchToRevision(rootBranch)
        libgit.createAndSwitchToOrphanBranch(OPSCONF_BRANCH_WORK)
        for root, dirnames, filenames in os.walk('.', topdown=True):
            if '.git' in dirnames:
                dirnames.remove('.git')

            for f in filenames:
                filepath = os.path.join(root, f)
                libgit.addOneFile(filepath)
                libgit.commitOneFile(filepath, "v1: First version for '{}'".format(filepath))
    else:
        libgit.createAndSwitchToOrphanBranch(OPSCONF_BRANCH_WORK)
        readmeFile = "README.md"
        with open("{}/{}".format(libgit.getGitRoot(), readmeFile), 'w') as f:
            f.write("# Readme\n")
            f.write("This repository is managed by opsconf.\n")
        libgit.addOneFile(readmeFile)
        libgit.commitOneFile(readmeFile, "v1: Add Readme")
        LOGGER.debug("Created first README")

    with open("{}/.opsconf".format(libgit.getGitRoot()), 'w') as f:
        # We only need to have it created
        pass

    LOGGER.debug("Created .opsconf file")
    libgit.addOneFile(".opsconf")
    libgit.commitOneFile(".opsconf", "v1: Initialized opsconf")
    # Keep the commit hash to initialize the other branches (cherry-pick)
    commitHash = libgit.logLastOneFile('.', outputFormat='%H')
    libgit.push(OPSCONF_BRANCH_WORK, newBranch=True)
    LOGGER.debug("Committed .opsconf file")
    for branch in [OPSCONF_BRANCH_VALID, OPSCONF_BRANCH_QUALIF]:
        # if the branch exists
        if libgit.existLocalBranch(branch):
            LOGGER.debug("Changing to branch: %s", branch)
            libgit.switchToRevision(branch)
            libgit.cherryPick(commitHash)
            libgit.push(branch)
            LOGGER.debug("Branch updated: %s", branch)
        else:
            LOGGER.debug("Creating branch: %s", branch)
            libgit.createAndSwitchToOrphanBranch(branch)
            libgit.resetTree(hard=True)
            libgit.cherryPick(commitHash)
            libgit.push(branch, newBranch=True)
            LOGGER.debug("Branch created: %s", branch)

    libgit.switchToRevision(OPSCONF_BRANCH_WORK)


def isCurrentBranchWork():
    """Check is the current branch is WORK.

    Returns:
        bool: True if the current branch is WORK. False otherwise.
    """
    currentBranch = libgit.getCurrentBranch()
    return currentBranch == OPSCONF_BRANCH_WORK


def isCurrentBranchQualif():
    """Check is the current branch is QUALIF.

    Returns:
        bool: True if the current branch is QUALIF. False otherwise.
    """
    currentBranch = libgit.getCurrentBranch()
    return currentBranch == OPSCONF_BRANCH_QUALIF


def isCurrentBranchValid():
    """Check is the current branch is VALID.

    Returns:
        bool: True if the current branch is VALID. False otherwise.
    """
    currentBranch = libgit.getCurrentBranch()
    return currentBranch == OPSCONF_BRANCH_VALID


def isOpsConfRepo():
    """Check if the current repository is an opsconf repository.

    Returns:
        bool: True if it is an opsconf repository. False otherwise.
    """
    libgit.fetch()
    if not (libgit.existRemoteBranch(OPSCONF_BRANCH_WORK) and
            libgit.existRemoteBranch(OPSCONF_BRANCH_QUALIF) and
            libgit.existRemoteBranch(OPSCONF_BRANCH_VALID)):
        LOGGER.debug("I cannot be an opsconf repo: Missing branches")
        return False
    if not libgit.existFileInRevision('.opsconf', OPSCONF_BRANCH_WORK, absolutePath=True):
        LOGGER.debug("I cannot be an opsconf repo: Missing .opsconf file")
        return False
    return True


def isExecutable(path):
    """Check if the file at 'path' is executable.

    Args:
        path (str): the path to test

    Returns:
        bool: True if executable, else False
    """
    return os.access(path, os.X_OK)


def hasUptodateHooks():
    """Check if the repository has up-to-date opsconf hooks.

    Returns:
        bool: True if the hooks are up-to-date. False otherwise.
    """
    hookdir = "{}/hooks".format(libgit.getGitDir())
    for hooksrc in os.listdir(OPSCONF_HOOKDIR):
        deployedHook = "{}/{}".format(hookdir, hooksrc)
        # If one hook from the share dir is not in the hooks
        if not os.path.isfile(deployedHook):
            return False
        if not isExecutable(deployedHook):
            LOGGER.error("The hooks are not executable. Maybe the partition is 'noexec'?")
            return False

        # If it is there but with wrong version
        with open(deployedHook, 'r') as f:
            hookVersion = None
            # OPSCONFVERSION=<version>
            for line in f.readline():
                if "OPSCONFVERSION" in line:
                    hookVersion = line.split('=')[1]
                    break

        if hookVersion is not None and hookVersion != OPSCONFVERSION:
            # One issue is enough to say if it has to be updated or not
            return False

    # If we reach here, everything is fine
    return True


def getDeletionHash(filename, revision):
    """Get the commit hash of the last deletion of a file.

    Args:
        filename (str): the path of the file of interest.
        revision (str): the revision from where to search for deletion.

    Returns:
        str: the hash of the commit in which the file was deleted.
    """
    try:
        return libgit.logLastOneFile(filename, revision, pattern="^{}".format(OPSCONF_PREFIX_REMOVED), outputFormat="%H")
    except libgit.GitNoLogError:
        return []

def getRevisionRange(filename, revision):
    """Get the revision range between the deletion of a file and a revision.

    This is used not to find revisions of a deleted file.
    If the file was never deleted, the revision is returned.

    Args:
        filename (str): the file of interest.
        revision (str): the revision to search from.

    Returns:
        str: a revision range.
    """
    deletionHash= getDeletionHash(filename, revision)
    if not deletionHash:
        revisionRange = revision
    else:
        revisionRange = "{}..{}".format(deletionHash, revision)
    return revisionRange


def prependFileVersion(filename):
    """Prepend to the commit message the version of the file ('v<VERSION>: ')

    The version is calculated as "previous version +1", so it only works
    because history is linear and without merges.
    The commit file is replaced by the new commit.

    Args:
        filename (string): the name of the file that contains the commit message.

    Raises:
        OpsconfFatalError: if something unexpected happened, this exception is raised.
    """
    if 'OPSCONF_BYPASS_CHECK' in os.environ:
        LOGGER.debug("By-passing checks and hooks")
        return

    with open(filename, 'r') as f:
        commitMessage = f.read()
    messageFirstLine = commitMessage.split('\n', maxsplit=1)[0]
    if messageFirstLine == "":
        raise OpsconfFatalError("Empty commit. Aborting")

    addedFileList = libgit.listCachedFiles()
    if len(addedFileList) == 1:
        addedFile = addedFileList[0]
    else:
        raise OpsconfFatalError("Only one file should have been added at once")

    revisionRange = getRevisionRange(addedFile, "HEAD")
    try:
        previousCommitSubject = libgit.logLastOneFile(addedFile, revisionRange, outputFormat='%s')
        previousCommitVersionNb = getVersionFromCommitMsg(previousCommitSubject)
    except libgit.GitNoLogError:
        previousCommitVersionNb = None

    if previousCommitVersionNb is None:
        previousCommitVersionNb = 0

    commitVersion = "v{}".format(previousCommitVersionNb + 1)
    with open(filename, 'w') as f:
        f.write("{}: {}".format(commitVersion, commitMessage))


def checkBranchIsWork():
    """Check if the current branch is WORK. Raises an exception otherwise.

    Raises:
        OpsconfFatalError: if the branch is not WORK, this exception is raised.

    Returns:
        bool: True if the current branch is WORK.
    """
    if 'OPSCONF_BYPASS_CHECK' in os.environ:
        return True

    if isCurrentBranchWork():
        return True
    else:
        raise OpsconfFatalError("You cannot commit on this branch. Change to {}".format(OPSCONF_BRANCH_WORK))


def getVersionFromCommitMsg(message):
    """Get the version from a commit message.

    Args:
        message (str): the commit message

    Returns:
        int or None: if a version was found, it is returned. Otherwise None.
    """
    # The subject is 'vXX: the message', with XX a number
    # We get vXX
    version = message.split(':', maxsplit=1)[0]
    # And now XX
    versionNb = version[1:]
    if versionNb.isdigit():
        return int(versionNb)
    else:
        return None


def getSubjectFromCommitMsg(message):
    """Get the subject from the commit message (i.e.: remove the version)

    Args:
        message (str): the commit message

    Returns:
        str: the subject of the commit
    """
    # The subject is 'vXX: the message',
    # We get 'the message'
    return message.split(' ', maxsplit=1)[1]


def checkBranchUpToDate():
    """Check if the local branch is in sync with the remote.

    Raises:
        OpsconfFatalError: if not, this exception is raised.

    Returns:
        bool: True if the local and remote branch are in sync.
    """
    libgit.fetch()
    localTip = libgit.getLocalBranchTip()
    remoteTip = libgit.getRemoteBranchTip()
    if localTip == remoteTip:
        LOGGER.debug("Repository is up-to-date")
        return True
    else:
        libgit.resetTree(mixed=True)
        raise OpsconfFatalError("The repository is not in sync. Aborting. Run 'opsconf sync'")


def checkCommitUniqueFile():
    """Check if a single file is committed.

    Raises:
        OpsconfFatalError: if more than one file are committed, this exception is raised.

    Returns:
        bool: True if only a single file is committed.
    """
    # Control that a commit only changes one file at a time.
    if libgit.isGitRepository():
        against = "HEAD"
    else:
        # Initial commit: diff against an empty tree object.
        against = libgit.getEmptyTreeObject()

    fileNb = len(libgit.listCachedFiles(against))
    LOGGER.debug("Number of files to commit: %s", fileNb)
    if fileNb == 0:
        raise OpsconfFatalError("Nothing to commit. Aborting.")
    elif fileNb > 1:
        libgit.resetTree(mixed=True)
        raise OpsconfFatalError("You are commiting more than one file. Aborting.")
    else:
        return True


def sync(localBranch, remote='origin'):
    """Synchronize the local branch with the remote.

    Args:
        localBranch (str): the branch to synchronize
        remote (str, optional): the remote to synchronize to. Defaults to 'origin'.

    Raises:
        OpsconfFatalError: if the synchronization cannot be automated, this exception is raised.
    """
    libgit.fetch(remote, branch=localBranch)
    libgit.pullNotes(remote)

    remoteBranch = "{}/{}".format(remote, localBranch)

    LOGGER.debug("Comparing %s and %s", remoteBranch, localBranch)
    if libgit.getLocalBranchTip() == libgit.getRemoteBranchTip():
        LOGGER.debug("Local and remote branch are in sync")
    elif libgit.isAncestor(remoteBranch, ancestor=localBranch):
        LOGGER.info("Local is behind the remote repository")
        libgit.merge(remoteBranch, ffOnly=True)
        LOGGER.info("Local was updated")
    elif libgit.isAncestor(localBranch, ancestor=remoteBranch):
        LOGGER.info("Local is ahead the remote repository")
        libgit.push(localBranch)
        LOGGER.info("Remote was updated")
    else:
        raise OpsconfFatalError("Local and remote branches have diverged. Call an expert !")


def doPush():
    """Push the current branch to the remote.
    """
    branch = libgit.getCurrentBranch()
    libgit.push(branch)


def retrieveVersion(sourceBranch, filename, version):
    """Bring the version of a file to the current branch.

    Args:
        sourceBranch (src): the branch where to search the version from.
        filename (str): the path of the file to search.
        version (int): the version to retrieve.

    Raises:
        OpsconfFatalError: if the retrieval is not possible, this exception is raised.

    Returns:
        str: the hash of the last created commit (or None if no commit was created).
    """
    # Bring a file version and its associated history from one branch to
    # the current one.
    revisionRange = getRevisionRange(filename, "HEAD")
    sourceBranchRevisionRange = getRevisionRange(filename, sourceBranch)

    try:
        lastVersionCommitMsg = libgit.logLastOneFile(filename, revisionRange, pattern=OPSCONF_PREFIX_PATTERN, outputFormat="%s")
        lastVersionNb = getVersionFromCommitMsg(lastVersionCommitMsg)
    except libgit.GitNoLogError:
        lastVersionNb = None

    if lastVersionNb is None:
        # case where the current file does not exist yet on the current branch
        # we pretend that the last commit on this file is HEAD
        LOGGER.debug("The file does not exist on this branch. Will take the first version: %s", filename)

        # we take the last commit of the repository
        lastHashBeforeRetrieval = libgit.logLastOneFile(libgit.getGitRoot(), "HEAD", outputFormat="%H")

        # get the first version from this file
        try:
            firstVersionHash = libgit.logLastOneFile(filename, sourceBranchRevisionRange, pattern="^v1: ", outputFormat="%H")
        except libgit.GitNoLogError:
            raise OpsconfFatalError("v1 of {} does not exist in branch {}.".format(filename, sourceBranch))

        # A cherry pick doesn't work here, because we do not know the history of the source branch
        # so we do as if v1 was the creation of the file
        firstVersionCommitMsg = libgit.logLastOneFile(filename, firstVersionHash, outputFormat='%B')
        firstVersionAuthor = libgit.logLastOneFile(filename, firstVersionHash, outputFormat='%an <%ae>')
        firstVersionDate = libgit.logLastOneFile(filename, firstVersionHash, outputFormat='%ci')

        libgit.bringFileFromRevision(filename, firstVersionHash)
        libgit.addOneFile(filename)
        os.environ['OPSCONF_BYPASS_CHECK'] = 'yes'
        libgit.commitOneFile(filename, message=firstVersionCommitMsg, author=firstVersionAuthor, date=firstVersionDate)
        del os.environ['OPSCONF_BYPASS_CHECK']

    elif lastVersionNb == version:
        # case where the current file already has the expected version
        # => Nothing to do
        LOGGER.info("%s is already in version %d. Nothing to do.", filename, version)
        return None

    elif lastVersionNb > version:
        # case where the current file has a greater version than the current one
        # => Error as versions must increase
        raise OpsconfFatalError("{} is already in a latter version than {}. Aborting.".format(filename, version))
    else:
        # get the last commit on the file, on our branch
        lastHashBeforeRetrieval = libgit.logLastOneFile(filename, revisionRange, pattern=OPSCONF_PREFIX_PATTERN, outputFormat="%H")

    lastVersionSubject = libgit.logLastOneFile(filename, revisionRange, pattern=OPSCONF_PREFIX_PATTERN, outputFormat="%s")
    try:
        lastHashSource = libgit.logLastOneFile(filename, sourceBranchRevisionRange, pattern=lastVersionSubject, outputFormat="%H")
        versionHashSource = libgit.logLastOneFile(filename, sourceBranchRevisionRange, pattern="^v{}: ".format(version), outputFormat="%H")
    except libgit.GitNoLogError:
        raise OpsconfFatalError("v{} of {} does not exist in branch {}".format(version, filename, sourceBranch))

    revisionToRetrieve = libgit.logOneFile(filename,
                                           "{}..{}".format(lastHashSource, versionHashSource),
                                           pattern=OPSCONF_PREFIX_PATTERN,
                                           outputFormat='%h'
                                          )
    # We want the history sorted by increasing date
    revisionToRetrieve.reverse()

    LOGGER.debug("Cherry-picking commits: %s", " ".join(revisionToRetrieve))
    for rev in revisionToRetrieve:
        libgit.cherryPick(rev)

    libgit.push(libgit.getCurrentBranch())

    pickedLog = libgit.logOneFile(filename, "{}..HEAD".format(lastHashBeforeRetrieval), outputFormat='%H %s')
    pickedLog.reverse()

    # we have a list of [ '%H %s' ], for instance [ 'e2...dfa v3: the reason of the change', ... ]
    # we want only the versions message (=%s) part
    pickedLogMessages = [ '    {}'.format(log.split(' ', 1)[1]) for log in pickedLog ]
    LOGGER.info("Retrieved changes of %s:\n%s", filename, '\n'.join(pickedLogMessages))
    # we want only the versions message (=%h) part of the last commit
    lastHashAfterRetrieval = pickedLog[-1].split(' ', 1)[0]
    return lastHashAfterRetrieval


def cleanLocalChange(filename):
    """Remove the local changes on a given filename.

    Args:
        filename (str): the file to clean.
    """
    libgit.bringFileFromRevision(filename, "HEAD")


def rollbackToVersion(filename, version, reason):
    """Rollback a file to a previous version.

    Args:
        filename (str): the file to rollback.
        version (int): the version to rollback to.
        reason (str): the reason of the rollback.

    Raises:
        OpsconfFatalError: if the rollback is not possible, this exception is raised.
    """
    branch = libgit.getCurrentBranch()
    if not libgit.existFileInRevision(filename, branch):
        raise OpsconfFatalError("This is not a file, or is not available in the branch {}: {}".format(branch, filename))
    revisionRange = getRevisionRange(filename, "HEAD")
    versionHash = libgit.logLastOneFile(filename, revisionRange, pattern="^v{}: ".format(version), outputFormat='%H')

    diff = libgit.diffOneFile(filename, fromRevision="HEAD", toRevision=versionHash)
    try:
        libgit.applyDiff(diff)
    except libgit.GitError:
        libgit.bringFileFromRevision(filename, 'HEAD')
        raise OpsconfFatalError("Rollback failed. Aborting.")
    libgit.commitOneFile(filename, message="{}\n\nRolled-back to v{}".format(reason, version))


def listAvailaibleVersions(branch, filename):
    """List all the versions of a file in a given branch.

    Args:
        branch (str): the branch where to search the versions.
        filename (str): the file of interest.

    Raises:
        OpsconfFatalError: if the file does not exist in the branch, this exception is raised.

    Returns:
        list of dict: the versions as: {'version': <int>, 'subject': <str>, 'tags': <list of str>}.
    """
    if not libgit.existFileInRevision(filename, branch):
        raise OpsconfFatalError("This is not a file, or is not available in the branch {}: {}".format(branch, filename))
    revisionRange = getRevisionRange(filename, branch)
    hashSubjects = libgit.logOneFile(filename, revisionRange, pattern=OPSCONF_PREFIX_PATTERN, outputFormat="%H,%s")

    versionList = []

    # get the commit hashes of the file version at all
    hashTagDict = {}
    for tag in libgit.listTags():
        try:
            hashTagDict[tag] = libgit.logLastOneFile(filename, tag, outputFormat="%H")
        except libgit.GitNoLogError:
        # the file did not exist at the time
            continue

    # For all hashlog from rawLogs (hash,log), we get the hash
    for item in hashSubjects:
        commitHash, message = item.split(',', maxsplit=1)

        versionLine = {
            'version': getVersionFromCommitMsg(message),
            'subject': getSubjectFromCommitMsg(message)
        }

        tagList = []
        for tag, tagHash in hashTagDict.items():
            if tagHash == commitHash:
                tagList.append(tag)
        versionLine['tags'] = tagList
        versionList.append(versionLine)
    return versionList


def listAllVersions(filename):
    """List the versions of a file in the branch WORK.

    Args:
        filename (str): the file of interest.

    Raises:
        OpsconfFatalError: if the file does not exist in the branch, this exception is raised.

    Returns:
        list of dict: the versions as: {'version': <int>, 'subject': <str>, 'tags': <list of str>}.
    """
    branch = OPSCONF_BRANCH_WORK
    return listAvailaibleVersions(branch, filename)


def listCurrentVersions(filename):
    """List all the versions of a file in the current branch.

    Args:
        filename (str): the file of interest.

    Raises:
        OpsconfFatalError: if the file does not exist in the branch, this exception is raised.

    Returns:
        list of dict: the versions as: {'version': <int>, 'subject': <str>, 'tags': <list of str>}.
    """
    branch = libgit.getCurrentBranch()
    return listAvailaibleVersions(branch, filename)


def showCurrentVersions(revision, withNotes=False):
    """Show the last versions of all the files in a revision.

    Args:
        revision (str): a revision (commit, branch, tag).
        withNotes (bool): whether to attach the 'git notes' with them. Defaults to False.

    Returns:
        list of dicts: each line as
                        {
                            'file': <str>,  # the path of the file
                            'version': <int>,  # the current version of the file
                            'removed': <bool>,  # True if the file was deleted from the WORK branch
                            'newer': <bool>,  # True if a newer version exists in teh WORK branch
                            'changed': <bool>,  # True if the file has non committed changes
                            'notes': <list of str>  # The list of notes associated to the version
                        }.
    """
    changedFileList = libgit.listChangedFiles()
    fileList = libgit.listAllFilesInRevision(revision)
    fileVersionList = []
    for filename in sorted(fileList):
        if filename == ".opsconf":
            continue

        lastCommitHashAndMsg = libgit.logLastOneFile(filename, revision, outputFormat='%H %s')
        lastCommitHash, lastCommitMsg = lastCommitHashAndMsg.split(' ', 1)
        lastVersion = getVersionFromCommitMsg(lastCommitMsg)

        lastCommitMsgInWork = libgit.logLastOneFile(filename, OPSCONF_BRANCH_WORK, outputFormat='%s')
        lastVersionInWork = getVersionFromCommitMsg(lastCommitMsgInWork)

        if withNotes:
            notes = libgit.getNotesFromCommit(lastCommitHash, topic=OPSCONF_PROMOTION_NOTE_TOPIC)
        else:
            notes = []

        fileVersion = {
            'file': filename,
            'version': lastVersion,
            'removed': False,
            'newer': False,
            'changed': False,
            'notes': notes
        }
        if filename in changedFileList:
            changedFileList.remove(filename)
            fileVersion['changed'] = True

        if lastVersionInWork is None:
            fileVersion['removed'] = True
        elif lastVersion != lastVersionInWork:
            fileVersion['newer'] = True
        else:
            pass

        fileVersionList.append(fileVersion)
    # The remaining files are the ones that were never committed in this branch
    for filename in changedFileList:
        fileVersionList.append(
            {
                'file': filename,
                'version': 0,
                'removed': False,
                'newer': False,
                'changed': True,
                'notes': []
            })

    return fileVersionList


def removeFile(filename, reason):
    """Remove a file from the repository.

    In this case the version of the changed is replaced by a specific prefix.
    (see OPSCONF_PREFIX_REMOVED)

    Args:
        filename (str): the path of the file to remove.
        reason (str): the reason of the deletion.

    Raises:
        OpsconfFatalError: if the file cannot be found in the current branch, this exception is raised.
    """
    checkBranchUpToDate()
    branch = libgit.getCurrentBranch()
    if not libgit.existFileInRevision(filename, branch):
        raise OpsconfFatalError("File not found in the branch {}: {}".format(branch, filename))

    libgit.removeOneFile(filename)
    os.environ['OPSCONF_BYPASS_CHECK'] = 'yes'
    libgit.commitOneFile(filename, message="{}{}".format(OPSCONF_PREFIX_REMOVED, reason))
    del os.environ['OPSCONF_BYPASS_CHECK']


def diffBetweenVersions(filename, version1=None, version2=None):
    """Get the diff between 2 versions of a gien file.

    Args:
        filename (str): the path of the file of interest
        version1 (int, optional): the version of reference. Defaults to None.
                                  If None, consider version1 as the last version of the file in this branch.
        version2 (int, optional): the version containing the changes. Defaults to None.
                                  If None, consider version2 as the current state of the file in the working
                                  directory.

    Returns:
        str: the diff (patch-like text).
    """
    if version1 is not None:
        try:
            h1 = libgit.logLastOneFile(filename, 'HEAD', pattern="^v{}: ".format(version1), outputFormat="%H")
        except libgit.GitNoLogError:
            raise OpsconfFatalError("Version {} not found in history for this file: {}".format(version1, filename))
    else:
        h1 = libgit.getLocalBranchTip()  # must be 'HEAD' because the file might not yet exist in the history.
    if version2 is not None:
        try:
            h2 = libgit.logLastOneFile(filename, 'HEAD', pattern="^v{}: ".format(version2), outputFormat="%H")
        except libgit.GitNoLogError:
            raise OpsconfFatalError("Version {} not found in history for this file: {}".format(version2, filename))
    else:
        h2 = None

    if not libgit.existFileInRevision(filename, h1):
        raise OpsconfFatalError('File not found in revision {}: {}'.format(h1, filename))

    # If we output to a tty, we want colors. If the output is piped, we want plain text
    # pylint: disable=simplifiable-if-statement
    if os.isatty(1):
        withColors = True
    else:
        withColors = False

    return libgit.diffOneFile(filename, h1, h2, withColors=withColors)


def promoteVersion(targetBranch, filename, version=None, message=None):
    """Promote a version of a file to the target branch.

    This function is used to 'qualify' or 'validate' a file version.

    Args:
        targetBranch (str): the branch where to bring the version.
        filename (str): the path of the file of interest.
        version (int, optional): the version to promote. Defaults to None. In this case,
                                        the last version from the file in the WORK branch is promoted.
        message (str, optional): a message to attach to the version promotion. Defaults to None.

    Raises:
        OpsconfFatalError: if the function is called from a branch different from targetBranch or WORK,
                           this exception is raised.
    """
    # If version is not given, get the last version from the WORK branch
    if version is None:
        lastCommitMsg = libgit.logLastOneFile(filename, OPSCONF_BRANCH_WORK,
                                              pattern=OPSCONF_PREFIX_PATTERN,
                                              outputFormat="%s")
        versionToPromote = getVersionFromCommitMsg(lastCommitMsg)
    else:
        versionToPromote = version

    if not libgit.existFileInRevision(filename, OPSCONF_BRANCH_WORK):
        raise OpsconfFatalError("{} does not exist in the current branch '{}' or is not a file".format(filename, targetBranch))

    lastHashAfterRetrieval = None
    if isCurrentBranchWork():
        # if on the WORK branch, move to the target branch to retrieve the file
        # then come back to the WORK branch
        currentPath = os.getcwd()
        currentBranch = OPSCONF_BRANCH_WORK

        LOGGER.debug("We are in branch %s", currentBranch)
        filePath = os.path.join(currentPath, filename)
        gitRootDir = libgit.getGitRoot()

        if filePath.startswith(gitRootDir):
            filePath.replace(gitRootDir, '', 1)

        try:
            # We first need to move the git root of the repository, in case it does not exist
            # in the WORK branch
            os.chdir(gitRootDir)
            libgit.switchToRevision(targetBranch)
            LOGGER.debug("We changed to branch %s", targetBranch)
            lastHashAfterRetrieval = retrieveVersion(OPSCONF_BRANCH_WORK, filename, versionToPromote)
        finally:
            # Move back to where we were at the beginning
            libgit.switchToRevision(currentBranch)
            LOGGER.debug("We are back in branch %s", currentBranch)
            os.chdir(currentPath)

    elif libgit.getCurrentBranch() == targetBranch:
        lastHashAfterRetrieval = retrieveVersion(OPSCONF_BRANCH_WORK, filename, versionToPromote)
    else:
        raise OpsconfFatalError("This action can only be done on branch {} or {}. Currently on branch {}. Aborting."
                                .format(OPSCONF_BRANCH_WORK, targetBranch, libgit.getCurrentBranch())
                               )

    if lastHashAfterRetrieval is not None and message is not None:
        libgit.addNoteToCommit(lastHashAfterRetrieval, message, topic=OPSCONF_PROMOTION_NOTE_TOPIC)
        libgit.pushNotes(topic=OPSCONF_PROMOTION_NOTE_TOPIC)
