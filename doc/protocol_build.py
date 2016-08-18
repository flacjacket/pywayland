import os
import tarfile
import six.moves.urllib as urllib

wayland_version = '1.11.0'
protocols_version = '1.7'

wayland_source = 'http://cgit.freedesktop.org/wayland/wayland/plain/protocol/wayland.xml?id={}'.format(wayland_version)
protocols_source = 'http://wayland.freedesktop.org/releases/wayland-protocols-{}.tar.xz'.format(protocols_version)


def _protocol_build(input_xml, output_dir):
    from pywayland.scanner import Scanner

    scanner = Scanner(input_xml)
    scanner.output(output_dir)


def wayland_build(output_dir):
    protocol_dest = 'wayland.xml'
    # first, we download the wayland.xml file
    urllib.request.urlretrieve(wayland_source, protocol_dest)
    # now we can build the main protocols
    _protocol_build(protocol_dest, output_dir)


def protocols_build(output_dir):
    protocol_dest = 'wayland-protocols-{}'.format(protocols_version)
    # download the protocols file and extract it
    urllib.request.urlretrieve(protocols_source, protocol_dest + '.tar.xz')
    with tarfile.open(protocol_dest + '.tar.xz') as f:
        f.extractall()

    # walk the directory and generate all the protocols
    for dirpath, _, filenames in os.walk(protocol_dest):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            # if the file is an xml, generate the protocol
            if ext == '.xml':
                _protocol_build(os.path.join(dirpath, filename), output_dir)
