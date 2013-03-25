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
        return node.stereotype('pyramid:configuration') is not None

registerScope('pyramid_configuration', 'uml2fs', [IPackage], pyramid_configuration)

class pyramid_static_view(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:static_view') is not None

registerScope('pyramid_static_view', 'uml2fs', [IClass], pyramid_static_view)

class pyramid_buildout(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:buildout') is not None

registerScope('pyramid_buildout', 'uml2fs', [IPackage], pyramid_buildout)

class view_function(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:view') is not None

registerScope('view_function', 'uml2fs', [IClass], view_function)

class view_method(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:view') is not None

registerScope('view_method', 'uml2fs', [IOperation], view_method)

class pyramid_config_scan(Scope):

    def __call__(self, node):
        return node.stereotype('pyramid:config_scan') is not None

registerScope('pyramid_config_scan', 'uml2fs', [IPackage], pyramid_config_scan)