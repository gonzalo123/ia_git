from unittest.mock import Mock

from lib.git_utils import _get_file_mode
from lib.models import Status


def test_get_file_mode_new_file():
    diff_mock = Mock()
    diff_mock.new_file = True
    assert _get_file_mode(diff_mock) == Status.CREATED


def test_get_file_mode_deleted_file():
    diff_mock = Mock()
    diff_mock.new_file = False
    diff_mock.deleted_file = True
    assert _get_file_mode(diff_mock) == Status.DELETED


def test_get_file_mode_copied_file():
    diff_mock = Mock()
    diff_mock.new_file = False
    diff_mock.deleted_file = False
    diff_mock.copied_file = True
    assert _get_file_mode(diff_mock) == Status.COPIED


def test_get_file_mode_modified_file():
    diff_mock = Mock()
    diff_mock.new_file = False
    diff_mock.deleted_file = False
    diff_mock.copied_file = False
    assert _get_file_mode(diff_mock) == Status.MODIFIED
