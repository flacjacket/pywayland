from .launcher import logger

# from pywayland.server import Client, DestroyListener
from pywayland.protocol.wayland import Compositor as CompositorProtocol, Subcompositor  # , Surface
# import pyudev

resources = []


def compositor_create_surface(compositor):
    logger.info('create surface')


def compositor_create_region(*args):
    logger.info('create region: %s', str(args))


def bind_compositor(resource):
    resources.append(resource)
    resource.listener['create_surface'] = compositor_create_surface
    resource.listener['create_region'] = compositor_create_region


def subcompositor_destroy(subcompositor):
    logger.info("subcompositor destroy")


def subcompositor_get_subsurface(*args):
    logger.info("get subsurface: %s", str(args))


def bind_subcompositor(resource):
    resources.append(resource)
    resource.listener["destroy"] = subcompositor_destroy
    resource.listener["get_subsurface"] = subcompositor_get_subsurface


def primary_client_destroyed(*args, **kwargs):
    pass


class Compositor(object):
    def __init__(self, display):
        compositor = CompositorProtocol.global_class(display, 4)
        compositor.bind_handler = bind_compositor

        subcompositor = Subcompositor.global_class(display, 1)
        subcompositor.bind_handler = bind_subcompositor

        self.globals_ = {
            'compositor': compositor,
            'subcompositor': subcompositor
        }
