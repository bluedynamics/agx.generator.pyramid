# -*- coding: utf-8 -*-
from zope.interface import implements
import agx.generator.pyramid
from agx.core.interfaces import IProfileLocation

class pyramid(object):

    implements(IProfileLocation)

    name = 'pyramid.profile.uml'
    package = agx.generator.pyramid