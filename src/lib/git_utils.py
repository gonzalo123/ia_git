import logging

from git.repo import Repo

from .models import Diff, DiffData, Status

logger = logging.getLogger(__name__)


def _get_file_mode(diff):
    if diff.new_file:
        return Status.CREATED
    elif diff.deleted_file:
        return Status.DELETED
    elif diff.copied_file:
        return Status.COPIED
    else:
        return Status.MODIFIED


def _build_diff_data(commit, diffs) -> DiffData:
    return DiffData(
        user=str(commit.author),
        date=commit.committed_datetime,
        diffs=[Diff(
            diff=str(diff),
            path=diff.b_path if diff.new_file else diff.a_path,
            status=_get_file_mode(diff)
        ) for diff in diffs]
    )


def get_diff(repo_path, commit_sha1, commit_sha2) -> DiffData:
    repo = Repo(repo_path)
    commit1, commit2 = repo.commit(commit_sha1), repo.commit(commit_sha2)

    diffs = commit1.diff(commit_sha2, create_patch=True)
    return _build_diff_data(commit2, diffs)


def get_current_diff(repo_path) -> DiffData:
    repo = Repo(repo_path)
    commit = repo.head.commit
    diffs = commit.diff(None, create_patch=True)

    return _build_diff_data(commit, diffs)
