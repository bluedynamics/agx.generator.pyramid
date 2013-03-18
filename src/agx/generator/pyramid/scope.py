# -*- coding: utf-8 -*-
from agx.core import (
    handler,
    Scope,
    registerScope,
    token,
)
from node.ext.uml.interfaces import (
    IOperation,
    IClass,
    IPackage,
    IInterface,
    IInterfaceRealization,
    IDependency,
    IProperty,
    IAssociation,
)

class pyramid_configuration(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:configuration') is not None and node.stereotype('pyegg:pyegg') is not None

registerScope('pyramid_configuration', 'uml2fs', None , pyramid_configuration)

class static_view(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:static_view') is not None

registerScope('pyramid_static_view', 'uml2fs', [IClass] , static_view)

class pyramid_view(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:view') is not None

registerScope('pyramid_view', 'uml2fs', [IClass] , pyramid_view)