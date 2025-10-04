#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Lubosz Sarnecki <lubosz@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from pywayland.client import Display
from pywayland.protocol.wayland.wl_registry import WlRegistryProxy
from pywayland.protocol.color_management_v1 import WpColorManagerV1
from pywayland.protocol.color_management_v1.wp_color_manager_v1 import WpColorManagerV1Proxy


class App:
    def __init__(self):
        self.color_manager = None
        self.render_intents = []
        self.features = []
        self.transfer_functions = []
        self.primaries = []


def color_manager_supported_intent_cb(color_manager: WpColorManagerV1Proxy, render_intent: int):
    app = color_manager.user_data
    app.render_intents.append(WpColorManagerV1.render_intent(render_intent))

def color_manager_supported_feature_cb(color_manager: WpColorManagerV1Proxy, feature: int):
    app = color_manager.user_data
    app.features.append(WpColorManagerV1.feature(feature))

def color_manager_supported_tf_named_cb(color_manager: WpColorManagerV1Proxy, transfer_function: int):
    app = color_manager.user_data
    app.transfer_functions.append(WpColorManagerV1.transfer_function(transfer_function))

def color_manager_supported_primaries_named_cb(color_manager: WpColorManagerV1Proxy, primaries: int):
    app = color_manager.user_data
    app.primaries.append(WpColorManagerV1.primaries(primaries))

def color_manager_done_cb(color_manager: WpColorManagerV1Proxy):
    app = color_manager.user_data

    print(f"Render intents ({len(app.render_intents)})")
    for render_intent in app.render_intents:
        print(f"\t{render_intent.name}")

    print(f"Features ({len(app.features)})")
    for feature in app.features:
        print(f"\t{feature.name}")

    print(f"Transfer Functions ({len(app.transfer_functions)})")
    for transfer_function in app.transfer_functions:
        print(f"\t{transfer_function.name}")

    print(f"Primaries ({len(app.primaries)})")
    for primaries in app.primaries:
        print(f"\t{primaries.name}")


def registry_global_cb(registry: WlRegistryProxy, name: int, interface: str, version: int):
    app = registry.user_data
    if interface == "wp_color_manager_v1":
        app.color_manager = registry.bind(name, WpColorManagerV1, version)
        app.color_manager.dispatcher["supported_intent"] = color_manager_supported_intent_cb
        app.color_manager.dispatcher["supported_feature"] = color_manager_supported_feature_cb
        app.color_manager.dispatcher["supported_tf_named"] = color_manager_supported_tf_named_cb
        app.color_manager.dispatcher["supported_primaries_named"] = color_manager_supported_primaries_named_cb
        app.color_manager.dispatcher["done"] = color_manager_done_cb
        app.color_manager.user_data = app

def main():
    app = App()

    display = Display()
    display.connect()

    registry = display.get_registry()
    registry.dispatcher["global"] = registry_global_cb
    registry.user_data = app

    display.dispatch(block=True)
    display.roundtrip()

    if app.color_manager is None:
        print("Compositor does not provide wp_color_manager_v1")

    display.disconnect()


if __name__ == "__main__":
    main()