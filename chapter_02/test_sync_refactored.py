from pathlib import Path
from sync_refactored import determine_actions


def test_when_a_file_exists_in_the_source_but_not_in_the_destination():
    src_hashes = {'hash1': 'fn1'}
    dst_hashes = {}
    actions = determine_actions(src_hashes, dst_hashes, Path("/src"), Path("/dst"))

    expected_actions = [('copy', Path("/src/fn1"), Path("/dst/fn1"))]
    assert list(actions) == expected_actions


def test_when_a_file_has_been_renamed_in_the_source():
    src_hashes = {'hash1': 'fn1'}
    dst_hashes = {'hash1': 'fn2'}
    actions = determine_actions(src_hashes, dst_hashes, Path("/src"), Path("/dst"))

    expected_actions = [('move', Path("/dst/fn2"), Path("/dst/fn1"))]
    assert list(actions) == expected_actions
