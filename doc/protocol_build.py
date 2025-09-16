import os
import subprocess
import tarfile
import urllib.request

wayland_version = "1.24.0"
protocols_version = "1.45"

wayland_source = f"https://cgit.freedesktop.org/wayland/wayland/plain/protocol/wayland.xml?id={wayland_version}"
protocols_source = f"https://gitlab.freedesktop.org/wayland/wayland-protocols/-/releases/{protocols_version}/downloads/wayland-protocols-{protocols_version}.tar.xz"


def _is_within_directory(directory, target):
    """Helper to check for CVE-2007-4559"""
    abs_directory = os.path.abspath(directory)
    abs_target = os.path.abspath(target)

    prefix = os.path.commonprefix([abs_directory, abs_target])

    return prefix == abs_directory


def _safe_extractall(tar, path=".", members=None, *, numeric_owner=False):
    """Helper to check for CVE-2007-4559"""
    for member in tar.getmembers():
        member_path = os.path.join(path, member.name)
        if not _is_within_directory(path, member_path):
            raise Exception("Attempted Path Traversal in Tar File")

    tar.extractall(path, members, numeric_owner=numeric_owner)


def protocols_build(output_dir):
    # first, we download the wayland.xml file
    wayland_file = "wayland.xml"
    urllib.request.urlretrieve(wayland_source, wayland_file)

    # download the protocols file and extract it
    protocol_dest = f"wayland-protocols-{protocols_version}"
    urllib.request.urlretrieve(protocols_source, protocol_dest + ".tar.xz")

    with tarfile.open(protocol_dest + ".tar.xz") as f:
        _safe_extractall(f)

    subprocess.run(
        [
            "python",
            "-m",
            "pywayland.scanner",
            "--with-protocols",
            "--output-dir",
            output_dir,
            "--input",
            wayland_file,
            "--input-protocols",
            protocol_dest,
        ]
    )
