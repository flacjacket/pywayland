import os
import tarfile
import urllib.request

wayland_version = "1.21.0"
protocols_version = "1.25"

wayland_source = "https://cgit.freedesktop.org/wayland/wayland/plain/protocol/wayland.xml?id={}".format(
    wayland_version
)
protocols_source = (
    "https://wayland.freedesktop.org/releases/wayland-protocols-{}.tar.xz".format(
        protocols_version
    )
)


def protocols_build(output_dir):
    from pywayland.scanner import Protocol

    # first, we download the wayland.xml file
    wayland_file = "wayland.xml"
    urllib.request.urlretrieve(wayland_source, wayland_file)

    # download the protocols file and extract it
    protocol_dest = "wayland-protocols-{}".format(protocols_version)
    urllib.request.urlretrieve(protocols_source, protocol_dest + ".tar.xz")
    with tarfile.open(protocol_dest + ".tar.xz") as f:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(f)

    # walk the directory and generate all the protocols
    protocol_files = [wayland_file] + sorted(
        [
            os.path.join(dirpath, filename)
            for dirpath, _, filenames in os.walk(protocol_dest)
            for filename in filenames
            if os.path.splitext(filename)[1] == ".xml"
        ],
        reverse=True,
    )

    protocols = [Protocol.parse_file(protocol_file) for protocol_file in protocol_files]
    protocol_imports = {
        interface.name: protocol.name
        for protocol in protocols
        for interface in protocol.interface
    }
    for protocol in protocols:
        protocol.output(output_dir, protocol_imports)
