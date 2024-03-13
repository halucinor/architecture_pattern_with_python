from sync_di import sync


class FakeFilesystem(list):

    def copy(self, source, dest):
        self.append(('copy', source, dest))

    def move(self, source, dest):
        self.append(('move', source, dest))

    def delete(self, path):
        self.append(('delete', path))


def test_when_a_file_exists_in_the_source_but_not_in_the_destination():
    source = {"sha1": "file1"}
    dest = {}
    filesystem = FakeFilesystem()

    reader = {"/src": source, "/dst": dest}
    sync(reader.pop, filesystem, "/src", "/dst")

    assert filesystem == [('copy', "/src/file1", "/dst/file1")]


def test_when_a_file_has_been_renamed_in_the_source():
    source = {"sha1": "renamed_file"}
    dest = {"sha1": "original_file"}
    filesystem = FakeFilesystem()

    reader = {"/src": source, "/dst": dest}
    sync(reader.pop, filesystem, "/src", "/dst")

    assert filesystem == [('move', "/dst/original_file", "/dst/renamed_file")]
