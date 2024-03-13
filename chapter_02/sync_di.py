def sync(reader, filesystem, source_root, dest_root):
    source_hashes = reader(source_root)
    dest_hashes = reader(dest_root)

    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            source_path = source_root + "/" + filename
            dest_path = dest_root + "/" + filename
            filesystem.copy(source_path, dest_path)

        elif dest_hashes[sha] != filename:
            old_dest_path = dest_root + "/" + dest_hashes[sha]
            new_dest_path = dest_root + "/" + filename
            filesystem.move(old_dest_path, new_dest_path)

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            filesystem.delete(dest_root / filename)
