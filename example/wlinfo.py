#!/usr/bin/env python
#
# Copyright (c) 2024 -- Lars Heuer
# All rights reserved.
#
# SPDX-License-Identifier: CC-PDDC
#
"""\
Prints information about a Wayland compositor.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import partial
from itertools import chain
from operator import itemgetter

from pywayland.client import Display
from pywayland.protocol.wayland import WlOutput, WlRegistry, WlSeat, WlShm


@dataclass
class Info:
    common: list = field(default_factory=list)
    seat: list = field(default_factory=list)
    output: list = field(default_factory=list)
    shm: list = field(default_factory=list)
    roundtrip_needed: bool = False

    def __str__(self) -> str:

        def stringify_interface(interface: str, version: int, name: int) -> str:
            return f"{interface:<{pad}}version: {version:2}, name: {name:2}"

        def stringify_head_tail(l: list) -> Iterator[str]:  # noqa: E741
            head, *tail = l
            yield stringify_interface(*head)
            yield from tail

        pad = len(max(map(itemgetter(0), self.common), key=len))

        return "\n".join(
            chain(
                stringify_head_tail(self.seat),
                stringify_head_tail(self.shm),
                stringify_head_tail(self.output),
                (
                    stringify_interface(*e)
                    for e in sorted(self.common, key=itemgetter(0))
                ),
            )
        )


def _add_interface_info(
    l: list, *, interface: str, version: int, name: int
) -> None:  # noqa: E741
    # Not building the complete output string here because
    # we need the length of the 1st element, see pad in Info.__str__()
    l.append((f"interface: '{interface}', ", version, name))


def add_seat_info(
    info: Info, registry: WlRegistry, id_num: int, interface: str, version: int
) -> None:

    def handle_capabilities(_, capabilities):
        caps = sorted(cap.name for cap in WlSeat.capability if capabilities & cap.value)
        append(f"capabilities: {' '.join(caps)}")

    def handle_name(_, name):
        append(f"name: {name}")

    _add_interface_info(info.seat, interface=interface, version=version, name=id_num)
    append = lambda s: info.seat.append(f"    {s}")  # noqa: E731
    seat = registry.bind(id_num, WlSeat, version)
    seat.dispatcher["name"] = handle_name
    seat.dispatcher["capabilities"] = handle_capabilities
    info.roundtrip_needed = True


def add_output_info(
    info: Info, registry: WlRegistry, id_num: int, interface: str, version: int
) -> None:

    def handle_geometry(
        _,
        x: int,
        y: int,
        width: int,
        height: int,
        subpixel: int,
        make: str,
        model: str,
        transform: int,
    ) -> None:
        subpixel_info = next(m.name for m in WlOutput.subpixel if m.value == subpixel)
        transform_info = next(
            m.name for m in WlOutput.transform if m.value == transform
        )
        append(f"x: {x}, y: {y}")
        append(f"physical_width: {width} mm, physical_height: {height} mm")
        append(f"make: '{make}', model: '{model}'")
        append(
            f"subpixel_orientation: {subpixel_info}, output_transform: {transform_info}"
        )

    def handle_scale(_, scale: int):
        append(f"scale: {scale}")

    def handle_name(_, name):
        append(f"name: {name}")

    def handle_description(_, description):
        append(f"description: {description}")

    def handle_mode(_, flags: int, width: int, height: int, refresh: int) -> None:
        flag_info = next(m.name for m in WlOutput.mode if flags & m.value)
        append("mode:")
        append_sub = lambda s: info.output.append(f"        {s}")  # noqa: E731
        append_sub(
            f"width: {width} px, height: {height} px, refresh: {refresh / 1000} Hz"
        )
        append_sub(f"flags: {flag_info}")

    _add_interface_info(info.output, interface=interface, version=version, name=id_num)
    append = lambda s: info.output.append(f"    {s}")  # noqa: E731
    output = registry.bind(id_num, WlOutput, version)
    output.dispatcher["name"] = handle_name
    output.dispatcher["description"] = handle_description
    output.dispatcher["geometry"] = handle_geometry
    output.dispatcher["scale"] = handle_scale
    output.dispatcher["mode"] = handle_mode
    info.roundtrip_needed = True


def add_shm_info(
    info: Info, registry: WlRegistry, id_num: int, interface: str, version: int
) -> None:

    def handle_format(_, fmt: int) -> None:
        format_info = next(f for f in WlShm.format if f.value == fmt)
        append(f"{hex(format_info.value)}: {format_info.name}")

    _add_interface_info(info.shm, interface=interface, version=version, name=id_num)
    append = lambda s: info.shm.append(f"    {s}")  # noqa: E731
    append("formats:")
    shm = registry.bind(id_num, WlShm, version)
    shm.dispatcher["format"] = handle_format
    info.roundtrip_needed = True


def handle_registry_global(
    info: Info, registry: WlRegistry, id_num: int, interface: str, version: int
) -> None:
    if interface in ("wl_seat", "wl_output", "wl_shm"):
        globals()[f"add_{interface[3:]}_info"](
            info, registry, id_num, interface, version
        )
    else:
        _add_interface_info(
            info.common, interface=interface, version=version, name=id_num
        )


def main():
    with Display() as display:
        registry = display.get_registry()
        info = Info()
        registry.dispatcher["global"] = partial(handle_registry_global, info)
        display.dispatch()
        while True:
            info.roundtrip_needed = False
            display.roundtrip()
            if not info.roundtrip_needed:
                break
        print(info)


if __name__ == "__main__":
    main()
