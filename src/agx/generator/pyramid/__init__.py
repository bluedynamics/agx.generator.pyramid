# -*- coding: utf-8 -*-
import generator, \
       scope

def register():
    """register this generator
    """
    import agx.generator.pyramid
    from agx.core.config import register_generator
    register_generator(agx.generator.pyramid)