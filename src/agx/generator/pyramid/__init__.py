# -*- coding: utf-8 -*-
import generator, \
       scope

_bleeding_edge_ = True

def register():
    """register this generator
    """
    import agx.generator.pyramid
    from agx.core.config import register_generator
    register_generator(agx.generator.pyramid)
