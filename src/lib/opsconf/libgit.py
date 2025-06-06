# SPDX-FileCopyrightText: 2025 Olivier Churlaud <olivier@churlaud.com>
# SPDX-FileCopyrightText: 2025 CNES
#
# SPDX-License-Identifier: MIT

"""Python wrapper around git operations that are usefull for opsconf"""

import logging
import os.path
import shlex
import subprocess

LOGGER = logging.getLogger('opsconf.libgit')

class GitError(RuntimeError):
    """The standard error for this libgit module.
    """
    pass


class GitNoLogError(GitError):
    """The error to raise when no log was found.
    """
    pass


def _runCmd(command, raiseException=True, cwd=None, inputContent=None, outputCleanup=True):
    """Run a shell command.

    Args:
        command (str or list of str): the command to run
        raiseException (bool, optional): whether to raise an exception or not if the command returns
                                         an errorcode that is not 0. Defaults to True.
        cwd (str, optional): the path where to run the command from. Defaults to None.
        inputContent (bytes, optional): a content to feed to the command through the stdin. Defaults to None.
        outputCleanup (bool, optional): whether to strip or not the newlines from the stdout and stderr.
                                           Defaults to True.

    Raises:
        GitError: if raiseException is True and the errorcode returned by the command is not 0 this exception
                  is raised.

    Returns:
        (str, str, int): the stdout, stderr and errorcode returned by the command.
    """
    if isinstance(command, str):
        splittedCommand = shlex.split(command)
    else:
        splittedCommand = command

    if inputContent is not None:
        stdin = subprocess.PIPE
    else:
        stdin = None

    LOGGER.debug("Running command: %s", splittedCommand)
    with subprocess.Popen(splittedCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=stdin, cwd=cwd) as proc:
        out, err = proc.communicate(input=inputContent)
        stdout = out.decode('utf-8')
        stderr = err.decode('utf-8')
        if outputCleanup:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()
        errno = proc.returncode

        LOGGER.debug('Return: %s', {'errno': errno, 'stdout': stdout, 'stderr': stderr})

    if raiseException and errno != 0:
        raise GitError("errno: {} ; {}".format(errno, stderr))
    return stdout, stderr, errno


def isGitRepository():
    """Check if this is a git repository.

    Returns:
        bool: True if this is a git repository.
    """
    _, _, errno = _runCmd(['git', 'rev-parse', '--is-inside-work-tree'], raiseException=False)
    return errno == 0


def isRepositoryEmpty():
    """Check if the git repository is empty.

    Returns:
        bool: True if the git repository is empty. False otherwise.
    """
    _, _, errno = _runCmd(['git', 'rev-parse', '--verify', 'HEAD'], raiseException=False)
    return errno != 0


def setConfig(key, value):
    """Set a configuration parameter.

    Args:
        key (str): the configuration key to set.
        value (str): the value to affect to the key.
    """
    _, _, _ = _runCmd(['git', 'config', '--local', key, value])

def isAncestor(child, ancestor):
    """Check if one revision is the ancestor of another.

    Args:
        child (str): the revision that would be the child of the other.
        ancestor (str): the revision that would be the ancestor of the other.

    Raises:
        GitError: if something goes wrong in the command, this exception is raised

    Returns:
        bool: True if 'ancestor' is the ancestor of 'child'. False otherwise.
    """
    _, stderr, errno = _runCmd(['git', 'merge-base', '--is-ancestor', ancestor, child], raiseException=False)
    if errno == 0:
        return True
    elif errno == 1:
        return False
    else:
        raise GitError("errno = {}, stderr = {}".format(errno, stderr))


def getGitDir():
    """Get the path .git directory from the repository.

    Returns:
        str: the path of the .git directory.
    """
    stdout, _, _ = _runCmd(['git', 'rev-parse', '--git-dir'])
    return stdout


def getGitRoot():
    """Get the root path of the repository.

    Returns:
        str: the root path of the repository.
    """
    stdout, _, _ = _runCmd(['git', 'rev-parse', '--show-toplevel'])
    return stdout


def getCurrentBranch():
    """Get the current branch (that is checked out).

    Returns:
        str: the current branch.
    """
    stdout, _, _ = _runCmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    return stdout


def existFileInRevision(filename, revision, absolutePath=False):
    """Check if the file exists in the revision (branch, tag, commit).

    Args:
        filename (str): the file path to search.
        revision (str): the revison (branch, tag, commit) where to search.
        absolutePath (bool): whether the path is absolute (from the root of the repo) or
            relative to the current directory.

    Returns:
        bool: True if the file was found. False otherwise.
    """

    gitrootdir = getGitRoot()
    if absolutePath:
        fullFilenamePath = filename
    else:
        relativeGitRootDir = os.path.relpath(gitrootdir)
        fullFilenamePath = os.path.relpath(filename, relativeGitRootDir)
    stdout, _, _ = _runCmd(['git', 'ls-tree', '-r', '--name-only', '--full-name',
                            '{}'.format(revision), gitrootdir])
    LOGGER.debug("looking for: %s", fullFilenamePath)
    return fullFilenamePath in stdout.splitlines()


def listChangedFiles():
    """List the repository's file that are not added nor committed.

    Returns:
        list of str: the file paths.
    """
    modified, _, _ = _runCmd(['git', 'ls-files', '-m'])
    untracked, _, _ = _runCmd(['git', 'ls-files', '-o', '--exclude-standard'])
    return modified.splitlines() + untracked.splitlines()


def listCachedFiles(againstRevision='HEAD'):
    """List the files that are currently cached.

    Args:
        againstRevision (str, optional): the revision to compare to. Defaults to 'HEAD'.

    Returns:
        list of str: the list of files that are currently cached.
    """
    stdout, _, _ = _runCmd(['git', 'diff', '--cached', '--name-only', againstRevision])
    return stdout.splitlines()


def listAllFilesInRevision(revision):
    """List the repository's files at the given revision.

    Args:
        revision (str): the revision to use.

    Returns:
        list of str: the file paths.
    """
    stdout, _, _ = _runCmd(['git', 'ls-tree', '-r', '--name-only', revision])
    return stdout.splitlines()


def getLocalBranchTip():
    """Get the revision of the local branch

    Returns:
        str: the hash of the revision
    """
    hashStr, _, _ = _runCmd(['git', 'rev-list', '-n', '1', 'HEAD'])
    return hashStr


def getRemoteBranchTip():
    """Get the revision of the remote branch of the current one.

    Returns:
        str: the hash of the revision
    """
    if isHeadABranch():
        hashStr, _, _ = _runCmd(['git', 'rev-parse', '@{u}'])
    else:
        # we are on a tag or commit, so we get the *local* hash
        hashStr, _, _ = _runCmd(['git', 'rev-list', '-n', '1', 'HEAD'])
    return hashStr


def getEmptyTreeObject():
    """Get an empty tree object (like if the repository was empty)

    Returns:
        str: an empty tree object hash
    """
    stdout, _, _ = _runCmd(['git', 'hash-object', '-t', 'tree', '/dev/null'])
    return stdout


def existRemoteBranch(branch):
    """Check if a remote branch exists.

    Args:
        branch (str): the branch to search.

    Returns:
        bool: True if the branch exists. False otherwise.
    """
    _, _, errno = _runCmd(['git', 'show-ref', 'refs/remotes/origin/{}'.format(branch)], raiseException=False)
    return errno == 0


def existLocalBranch(branch):
    """Check if a local branch exists.

    Args:
        branch (str): the branch to search.

    Returns:
        bool: True if the branch exists. False otherwise.
    """
    _, _, errno = _runCmd(['git', 'show-ref', 'refs/heads/{}'.format(branch)], raiseException=False)
    return errno == 0


def initRepository():
    """Initialize the repository.

    Raises:
        GitError: if the repository was already initialized, this exception is raised.
    """
    if isGitRepository():
        raise GitError("This is already a git repository. Not doing anything.")
    _runCmd(['git', 'init'])


def fetch(remote=None, branch=None):
    """Fetch the distant repositories

    Args:
        remote (str, optional): the remote to fetch. Defaults to None.
        branch (str, optional): the branch to fetch. Defaults to None.

    Raises:
        ValueError: if the branch is given without remote, this exception is raised
    """
    cmd = ['git', 'fetch']
    if remote is None and branch is not None:
        raise ValueError("Branch can be set only if remote is set")
    if remote is not None:
        cmd.append(remote)
    if branch is not None:
        cmd.append(branch)

    _runCmd(cmd)


def isRevisionABranch(revision):
    """Check if a revision is a branch.

    Args:
        revision (str): the revision to check.

    Returns:
        bool: True if the revision is a branch, False otherwise.
    """
    _, _, errno = _runCmd(['git', 'show-ref', '--verify', 'refs/heads/{}'.format(str(revision))], raiseException=False)
    return errno == 0


def isHeadABranch():
    """Check if the head is a branch (if not, it's in a detached state)

    Returns:
        bool: True if it's a branch, False if we are in a detached state (tag, commit)
    """
    _, _, errno = _runCmd(['git', 'symbolic-ref', '-q', 'HEAD'], raiseException=False)
    return errno == 0


def switchToRevision(revision):
    """Switch to a revision.

    Args:
        revision (str): the revision to switch to (branch, tag, commit).
    """

    if isRevisionABranch(revision):
        _runCmd(['git', 'switch', str(revision)])
    else:
        _runCmd(['git', 'switch', '--detach', str(revision)])


def bringFileFromRevision(filename, revision):
    """Bring a file to the repository as it was in a given revision.

    Args:
        filename (str): the path of the file to bring.
        revision (str): the revision where to retrieve it.
    """
    _runCmd(['git', 'restore', '--source' ,str(revision), filename])


def createBranch(branch):
    """Create a branch.

    Args:
        branch (str): the name of the branch to create.
    """
    _runCmd(['git', 'branch', branch])


def createAndSwitchToOrphanBranch(branch):
    """Create an orphan branch and switch to it.

    Args:
        branch (str): the name of the branch to create
    """
    _runCmd(['git', 'checkout', '--orphan', branch])


def addOneFile(filename):
    """Add a single file to the index.

    This command does not commit this change.

    Args:
        filename (str): path of the file to add.
    """
    _runCmd(['git', 'add', filename])


def removeOneFile(filename):
    """Remove a single file from the repository.

    This command does not commit this change.

    Args:
        filename (str): the path of the file to remove.
    """
    _runCmd(['git', 'rm', filename])


def commitOneFile(filename, message, date=None, author=None):
    """Commit the changes on a single file.

    Args:
        filename (str): the path of the file to commit.
        message (str): the commit message.
        date (str, optional): the date of the commit. Defaults to None.
                              If not given, the current date is used
        author (str, optional): the author of the commit. Defaults to None.
                                If not given, the author configured in git is used
    """
    cmd = ['git', 'commit', '-m', message]
    if date is not None:
        cmd += ['--date', date]
    if author is not None:
        cmd += ['--author', author]

    cmd += [filename]
    _runCmd(cmd)


def addNoteToCommit(commitHash, noteMessage, topic="commits"):
    """Add a note to a given commit.

    Args:
        commitHash (str): the commit hash to which to add a note.
        noteMessage (str): the text from the note.
        topic (str, optional): the notes topic (refs/notes/{topic}). Defaults to 'commits'
    """
    _runCmd(['git', 'notes', '--ref', topic, 'append', '-m', noteMessage, commitHash])


def pushNotes(remote="origin", topic="commits"):
    """Push the notes to the remote

    Args:
        remote (str, optional): the remote where to push the notes. Defaults to 'origin'.
        topic (str, optional): the notes topic (refs/notes/{topic}). Defaults to 'commits'
    """
    _runCmd(['git', 'push', remote, 'refs/notes/{}'.format(topic)])


def pullNotes(remote="origin"):
    """Pull the notes to the remote

    Args:
        remote (str, optional): the remote where to push the notes. Defaults to 'origin'.
    """
    _runCmd(['git', 'fetch', remote, 'refs/notes/*:refs/notes/*'])


def getNotesFromCommit(commitHash, topic="commits"):
    """Get the notes from a given commit.

    Args:
        commitHash (str): the hash of the commit from which to get the notes.
        topic (str, optional): the notes topic (refs/notes/{topic}). Defaults to 'commits'

    Returns:
        list of str: the notes of the commit (split by '\n\n')
    """
    # if the commit has no note, the command returns 1
    # with raiseException=False, stdout will be empty
    stdout, _, _ = _runCmd(['git', 'notes', '--ref', topic, 'show', commitHash], raiseException=False)
    return stdout.split('\n\n')


def resetTree(hard=False, soft=False, mixed=False):
    """Reset the repository to it's HEAD state.

    See the help of the command `git reset` for more details on the behavior.

    Args:
        hard (bool, optional): discard all changes from the index and the working directory.
                               Defaults to False.
        soft (bool, optional): undo the last commit, but keep the changes in the index. Defaults to False.
        mixed (bool, optional): remove all the changes from the index, but keep them in the working directory.
                                Defaults to False.

    Raises:
        ValueError: if more than one option is set to True, this exception is raised.
    """
    cmd = ['git', 'reset']
    if sum([hard, soft, mixed]) > 1:
        raise ValueError("gitReset: only one of 'hard' or 'soft' or 'mixed' can be True")
    if hard:
        cmd.append('--hard')
    if soft:
        cmd.append('--soft')
    if mixed:
        cmd.append('--mixed')  # default value for git reset
    _runCmd(cmd)


def cherryPick(gitHash):
    """Cherry pick a commit.

    Args:
        gitHash (str): the hash of the commit to cherry-pick.
    """
    _runCmd(['git', 'cherry-pick', gitHash])


def merge(otherBranch, ffOnly=None):
    """Merge an other branch to the current one.

    Args:
        otherBranch (str): the other branch to merge in the current one.
        ffOnly (bool, optional): whether the merge should be fast-forward or not. Defaults to None.
                                If not set, the configured behavior of git is used.
    """
    cmd = ['git', 'merge', otherBranch]
    if ffOnly is not None and ffOnly:
        cmd.append('--ff-only')
    _runCmd(cmd)


def push(branch, newBranch=False, remote='origin'):
    """Push the local changes to the remote.

    Args:
        branch (str): the branch to push.
        newBranch (bool, optional): whether the branch to push exists or not in the remote. Defaults to False.
        remote (str, optional): the remote to push to. Defaults to 'origin'.
    """
    if newBranch:
        _runCmd(['git', 'push', '-u', remote, branch])
    else:
        _runCmd(['git', 'push', remote, branch])


def pushTag(tag, remote='origin'):
    """Push a tag to the remote.

    Args:
        tag (str): the name of the tag.
        remote (str, optional): the remote to push to. Defaults to 'origin'.
    """
    _runCmd(['git', 'push', remote, tag])


def setTag(tag, message=None):
    """Set a tag to the current HEAD.

    Args:
        tag (str): name of the tag.
        message (str, optional): description of the tag. Defaults to None. If a message is given, the tag
                                 is annotated. If not, the tag is simple.
    """
    if message is None:
        _runCmd(['git', 'tag', tag])
    else:
        _runCmd(['git', 'tag', '-a', tag, '-m', message])


def listTags():
    """List the tags

    Returns:
        list of str: the tags
    """
    stdout, _, _ = _runCmd(['git', 'tag', '-l'])
    return stdout.splitlines()


def logOneFile(filename, revision='HEAD', pattern=None, outputFormat='%h %s', logCount=None):
    """Get the history logs of a single file.

    Args:
        filename (str): the path of the file of interest.
        revision (str, optional): the revision in which to get the history logs. Defaults to 'HEAD'.
        pattern (str, optional): the pattern of logs to filter. Defaults to None.
        outputFormat (str, optional): the format in which the logs shall be returned. Defaults to '%h %s'.
        logCount (_type_, optional): the number of logs to return. Defaults to None.

    Returns:
        list of str: the history log
    """
    cmd = ['git', 'log', '--format={}'.format(outputFormat)]
    if logCount is not None:
        cmd += ['-n', str(logCount)]
    if pattern is not None:
        cmd += ['--grep', pattern]
    cmd += [revision, '--', filename]
    stdout, _, _ = _runCmd(cmd)
    return stdout.splitlines()


def logLastOneFile(filename, revision='HEAD', pattern=None, outputFormat='%h %s'):
    """Get the last history logs of a single file (matching the filter).

    This is the same as calling `logOneFile()` with logCount=1.

    Args:
        filename (str): the path of the file of interest.
        revision (str, optional): the revision in which to get the history logs. Defaults to 'HEAD'.
        pattern (str, optional): the pattern of logs to filter. Defaults to None.
        outputFormat (str, optional): the format in which the logs shall be returned. Defaults to '%h %s'.

    Returns:
        list of str: the history log.
    """
    logs = logOneFile(filename, revision, pattern, outputFormat, logCount=1)
    if len(logs) == 0:
        raise GitNoLogError("No log was found for {} in {}, with pattern {}".format(filename, revision, pattern))
    else:
        return logs[0]


def diffOneFile(filename, fromRevision='HEAD', toRevision=None, withColors=False):
    """Get the diff of a file between 2 revisions.

    Args:
        filename (str): the file on which to apply the diff.
        fromRevision (str, optional): the revision used as reference. Defaults to 'HEAD'.
        toRevision (str, optional): the revision used as the modification. Defaults to None.
                                    If None, it takes the working directory state.

    Returns:
        str: the patch-like result of the diff.
    """
    if toRevision is None:
        revision = fromRevision
    else:
        revision = "{}..{}".format(fromRevision, toRevision)

    cmd = ['git', 'diff']
    if withColors:
        cmd += ['--color=always']
    cmd += [revision, '--', filename]

    stdout, _, _ = _runCmd(cmd, outputCleanup=False)
    return stdout


def applyDiff(diff):
    """Apply a patch-like string to the repository.

    Args:
        diff (str or bytes): the patch-like text.
    """
    if isinstance(diff, str):
        diffBytes = diff.encode('utf8')
    else:
        diffBytes = diff
    _runCmd(['git', 'apply'], inputContent=diffBytes)
