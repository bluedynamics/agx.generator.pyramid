# -*- coding: utf-8 -*-
import os
import shutil
from agx.generator.pyegg.utils import (
    class_base_name,
    implicit_dotted_path,
)
from agx.core.util import (
    read_target_node,
    dotted_path,
)
from agx.core.interfaces import IScope
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
from node.ext.python.interfaces import IModule
from node.ext.python.utils import Imports
from node.ext.python import Function, Block
from node.ext.uml.utils import TaggedValues
import agx

@handler('generate_configuration', 'uml2fs', 'semanticsgenerator',
         'pyramid_configuration')
def generate_configuration(self, source, target):
    tgt = read_target_node(source, target.target)
    
    if IModule.providedBy(tgt):
        # target is a module, then its ok
        module = tgt
    else:
        # fetch __init__.py
        module = tgt['__init__.py']
        
    tok = token('pyramid_configuration', True,
              imports=[], static_views=[], scans=[])
    
    imps = Imports(module)
    imps.set('wsgiref.simple_server', 'make_server')
    imps.set('pyramid.config', 'Configurator')
    
    # create a function main if not present
    if 'main' not in [f.functionname for f in module.functions()]:
        func = Function('main')
        module.insertafterimports(func)
    
    main = module.functions(name='main')[0]
    if not main.blocks('Configurator'):
        main.insertfirst(Block('config = Configurator()'))
        
    
    
    # do the configurator stuff
    mainblock = main.blocks('Configurator')[0]

    #insert app stuff at end of block
    mainblock.insertlineafter("app = config.make_wsgi_app()" ,None, ifnotpresent=True)
    mainblock.insertlineafter("return app" ,'make_wsgi_app', ifnotpresent=True)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    #static views
    for sv in tok.static_views:
        mainblock.insertlineafter('''config.add_static_view('%s', '%s/',%s)''' % \
                (sv[0], sv[1], sv[2]), 'Configurator', ifnotpresent=True)
        
    #scans
    for scan in tok.scans:
        if scan:
            mainblock.insertlineafter("config.scan('%s')" % scan,'add_static_view', ifnotpresent=True)
        else:
            mainblock.insertlineafter("config.scan()" ,'add_static_view', ifnotpresent=True)
            
            
    if not module.blocks('__main__'):
        module.insertlast(Block('''if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()'''))

@handler('handle_setup', 'uml2fs', 'semanticsgenerator', 'pyramid_configuration')
def handle_setup(self, source, target):
    print "handle_setup"

@handler('generate_ini_files', 'uml2fs', 'semanticsgenerator',
         'pyramid_configuration')
def generate_ini_files(self, source, target):
    print "generate_ini_files"

@handler('generate_static_view', 'uml2fs', 'connectorgenerator',
         'pyramid_static_view')
def generate_static_view(self, source, target):
    directory = read_target_node(source, target.target)
    tok = token('pyramid_configuration', True, static_views=[])
    tgv = TaggedValues(source)
    
    path = source.name
    url = tgv.direct('url', 'pyramid:static_view', source.name)
    tok.static_views.append([url, path, ''])
    
    # if from_template is given, copy the files from the given 
    # resource template into the target
    from_template = tgv.direct('from_template', 'pyramid:static_view', None)  
    if from_template:
        basepath = os.path.dirname(agx.generator.pyramid.__file__)
        srcpath = os.path.join(basepath, 'resources', 'static_templates', from_template)
        tgtpath = os.path.join(*directory.fs_path)
        if not os.path.exists(tgtpath):
            os.makedirs(tgtpath)
            
        # copy over the files
        flist = os.listdir(srcpath)
        for f in flist:
            srcfile = os.path.join(srcpath, f)
            tgtfile = os.path.join(tgtpath, f)
            if not os.path.exists(tgtfile):
                if os.path.isdir(srcfile):
                    shutil.copytree(srcfile, tgtfile)
                else:
                    shutil.copy(srcfile, tgtfile)

@handler('generate_docs', 'uml2fs', 'semanticsgenerator',
         'pyramid_configuration')
def generate_docs(self, source, target):
    print NotImplementedError("generate_docs")

@handler('generate_view', 'uml2fs', 'hierarchygenerator', 'pyramid_view')
def generate_view(self, source, target):
    raise NotImplementedError("stub generated by AGX.")

@handler('generate_buildout', 'uml2fs', 'semanticsgenerator', 'pyramid_buildout')
def generate_buildout(self, source, target):
    raise NotImplementedError("stub generated by AGX.")

@handler('mark_config_scan', 'uml2fs', 'connectorgenerator',
         'pyramid_config_scan')
def mark_config_scan(self, source, target):
    tok=token('pyramid_configuration',True,scans=[])
    if source.stereotype('pyegg:pyegg'):
        tok.scans.append('')
    else:
        tok.scans.append(source.name)

