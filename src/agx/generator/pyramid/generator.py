# -*- coding: utf-8 -*-
import os
import shutil
from zope.component import ComponentLookupError
from agx.generator.pyegg.utils import (
    class_base_name,
    implicit_dotted_path,
    import_if_necessary,
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
from node.ext.python.interfaces import IModule, IClass as IPythonClass
from node.ext.python.utils import Imports
from node.ext.python import Function, Block, Decorator, Attribute
from node.ext.uml.utils import TaggedValues
from node.ext.template import JinjaTemplate, DTMLTemplate
from node.ext.directory import (
    Directory,
    File,
    )
import agx

def templatepath(name):
    return os.path.join(os.path.dirname(__file__), 'resources', 'templates', '%s' % name)

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
        func.args = ['global_config', '**settings']
        module.insertafterimports(func)
    
    main = module.functions(name='main')[0]
    try:
        srtok = token('site_root', False)
        bootstrap = srtok.bootstrap
    except ComponentLookupError:
        bootstrap = None
        
    if not main.blocks('Configurator'):
        if bootstrap:
            import_if_necessary(module, bootstrap)
            main.insertfirst(Block('config = Configurator(root_factory=bootstrap)'))
        else:
            main.insertfirst(Block('config = Configurator()'))
        
    
    
    # do the configurator stuff
    mainblock = main.blocks('Configurator')[0]
    
    # importmes
    imptok = token('pyramid_importmes', True, packages=[])
    for pack in imptok.packages:
        mainblock.insertlineafter( "config.include('%s')" % pack,'Configurator', ifnotpresent=True)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    # static views
    for sv in tok.static_views:
        mainblock.insertlineafter('''config.add_static_view('%s', '%s/',%s)''' % \
                (sv[0], sv[1], sv[2]), 'Configurator', ifnotpresent=True)
        
    # scans
    for scan in tok.scans:
        if scan:
            mainblock.insertlineafter("config.scan('%s')" % scan, 'add_static_view', ifnotpresent=True)
        else:
            mainblock.insertlineafter("config.scan()" , 'add_static_view', ifnotpresent=True)
            
    # insert app stuff at end of block
    mainblock.appendline("app = config.make_wsgi_app()", ifnotpresent=True)
    mainblock.appendline("return app", ifnotpresent=True)
             
    if not module.blocks('__main__'):
        module.insertlast(Block('''if __name__ == '__main__':
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()'''))

@handler('handle_setup', 'uml2fs', 'semanticsgenerator', 'pyramid_configuration')
def handle_setup(self, source, target):
    print "handle_setup"

@handler('generate_ini_files', 'uml2fs', 'hierarchygenerator',
         'pyramid_configuration', order=11)
def generate_ini_files(self, source, target):
    print "generate_ini_files"
    egg = target.anchor
    
    for name in ['development.ini']:
        egg.factories[name] = JinjaTemplate
            
        if name not in egg.keys():
            egg[name] = JinjaTemplate()
            egg[name].template = templatepath(name + '.jinja')
            egg[name].params = {'package':source.name,
                                        'host':'0.0.0.0',
                                        'port':'8080'}
    
    ept = """[paste.app_factory]
        main = %s:main"""
    tok = token('entry_points', True, defs=[])
    tok.defs.append(ept % dotted_path(source))

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

@handler('mark_config_scan', 'uml2fs', 'connectorgenerator',
         'pyramid_config_scan')
def mark_config_scan(self, source, target):
    tok = token('pyramid_configuration', True, scans=[])
    if source.stereotype('pyegg:pyegg'):
        tok.scans.append('')
    else:
        tok.scans.append('.' + source.name)

@handler('generate_docs', 'uml2fs', 'semanticsgenerator',
         'pyramid_configuration')
def generate_docs(self, source, target):
    print NotImplementedError("generate docs.")

def create_template_file(tdir, template, from_template=None, template_code=None):
    splitted = template.split('/')
    fname = splitted[-1]
    if len(splitted) > 1:  # we have to check/create containing dirs
        for dname in splitted[:-1]:
            if not tdir.has_key(dname):
                # lets create it
                new = Directory(dname)
                tdir[dname] = new
                tdir = tdir
    
            tdir = tdir[dname]
    
    
    # get the template-template name
    if from_template and from_template != 'none':
        print 'getting template template:', from_template
        # and create the pagetemplate from the template-template
        if fname not in tdir.keys():
            templ = DTMLTemplate()
            tdir.factories[fname] = JinjaTemplate
            templ.template = templatepath(from_template) + '.dtml'
            tdir[fname] = templ
    else:
        # if template code is given, fill it into the file
        if template_code:
            if fname not in tdir.keys():
                file = File()
                file.data = template_code
                tdir[fname] = file
                

@handler('generate_view_function', 'uml2fs', 'connectorgenerator',
         'view_function')
def generate_view_function(self, source, target):
    tgv = TaggedValues(source)
    func = read_target_node(source, target.target)
    
    if IPythonClass.providedBy(func.parent):
        # We have a method
        module = func.parent.parent
        klass = source.parent
        token(str(klass.uuid), True, has_view_methods=True)
        is_method = True
    else:
        module = func.parent
        is_method = False
    
    imps = Imports(module)
        
    funccode = "return Response('this is the stub for view %s')" % source.name
    
    # name of view
    route_name = tgv.direct('route_name', 'pyramid:view', source.name)
    if route_name == '/':
        route_name = ''
        
    if not func.decorators('view_config'):
        func.insertfirst(Decorator('view_config'))
    
    dec = func.decorators('view_config')[0]
    dec.kwargs['name'] = "'%s'" % route_name
    
    # necessary imports
    imps.set('pyramid.view', 'view_config')
    
    # the request argument
    if not is_method and not 'request' in func.args:
        func.args.append('request')
        
    # create the page template
    template = tgv.direct('template', 'pyramid:view', None)
    # template from which the template file will be generated
    from_template = tgv.direct('from_template', 'pyramid:view', None)
    if from_template and from_template != 'none' and not template:
        template = source.name + '.pt'
        
    print 'template name:', template, from_template
    if template:
        tdir = module.parent
        # set the renderer parameter based on the template name
        dec.kwargs['renderer'] = "'%s'" % template
    
        # create the template in target dir
        template_code = tgv.direct('template_code', 'pyramid:view', None)
        create_template_file(tdir, template, from_template, template_code=template_code and template_code.strip())   
                 
        # generate default function body
        funccode = '''return {"page_title": "%s"}''' % source.name
    
    # if given set the renderer parameter
    renderer = tgv.direct('renderer', 'pyramid:view', None)
    if renderer and not dec.kwargs.get('renderer'):
        dec.kwargs['renderer'] = "'%s'" % renderer
        
    # if view function is empty, make a default code displaying info
    if not func.blocks():
        func.insertfirst(Block(funccode))
        imps.set('pyramid.response', 'Response')

@handler('generate_buildout', 'uml2fs', 'semanticsgenerator', 'pyramid_buildout',
         order=11)
def generate_buildout(self, source, target):
    egg = target.anchor
    
    egg.factories['buildout.cfg'] = JinjaTemplate
    egg.factories['versions.cfg'] = JinjaTemplate
    egg.factories['bootstrap.py'] = JinjaTemplate
    
    if 'versions.cfg' not in egg:
        egg['versions.cfg'] = JinjaTemplate()
        egg['versions.cfg'].template = templatepath('versions.cfg.jinja')
        egg['versions.cfg'].params = {}
        
    if 'buildout.cfg' not in egg.keys():
        egg['buildout.cfg'] = JinjaTemplate()
        egg['buildout.cfg'].template = templatepath('buildout.cfg.jinja')
        egg['buildout.cfg'].params = {'package':source.name}
        
    if 'bootstrap.py' not in egg.keys():
        egg['bootstrap.py'] = JinjaTemplate()
        egg['bootstrap.py'].template = templatepath('bootstrap.py.jinja')
        egg['bootstrap.py'].params = {}

@handler('mark_view_as_function', 'uml2fs', 'hierarchygenerator',
         'view_function', order=8)
def mark_view_as_function(self, source, target):
    token(str(source.uuid), True, is_function=True)

@handler('generate_view_class', 'uml2fs', 'semanticsgenerator', 'pyclass')
def generate_view_class(self, source, target):
    targetklass = read_target_node(source, target.target)
    try:
        module = targetklass.parent
    except AttributeError:
        # if there is no parent, this handler is not responsible
        return
    tdir = module.parent
    
    try:
        tok = token(str(source.uuid), False)
        has_view_methods = tok.has_view_methods
    except:
        has_view_methods = False
        
    view_class = source.stereotype('pyramid:view_class')
    
    # create init method
    if view_class or has_view_methods:
        inits = targetklass.functions('__init__')
        if inits:
            init = inits[0]
        else:
            init = Function('__init__')
            targetklass.insertfirst(init)
        
        # import pdb;pdb.set_trace()    
        init.args = ['context', 'request']
    
        if not init.blocks('self.request'):
            init.insertfirst(Block('self.request = request'))
        if not init.blocks('self.context'):
            init.insertfirst(Block('self.context = context'))
            
        # if its a view_class create the global_template
        if view_class:
            gtemplate = view_class.taggedvalue('global_template').value
            from_gtemplate = view_class.taggedvalue('from_global_template').value
            create_template_file(tdir, gtemplate, from_gtemplate)
            imps = Imports(module)
            imps.set('pyramid.renderers', 'get_renderer')
            
            if not init.blocks('global_template'):
                init.insertlast(Block('renderer = get_renderer("%s")' % gtemplate))
                init.insertlast(Block('self.global_template = renderer.implementation()'))
                init.insertlast(Block('self.macros = self.global_template.macros'))

@handler('generate_sqlalchemy_config', 'uml2fs', 'pyramid_semanticsgenerator',
         'sqlalchemy_package')
def generate_sqlalchemy_config(self, source, target):
    tgt = read_target_node(source, target.target)
    if IModule.providedBy(tgt):
        # target is a module, then its ok
        module = tgt
        target_dir = module.parent
    else:
        # fetch __init__.py
        module = tgt['__init__.py']
        target_dir = tgt
    
    
    # first lets create sqla_config.py that does all the config situps
    fname = 'sqla_config.py'
    package_name = implicit_dotted_path(source)
    templ = JinjaTemplate()
    target_dir.factories[fname] = JinjaTemplate
    templ.template = templatepath(fname) + '.jinja'
    target_dir[fname] = templ
    target_dir[fname].params = {'engine_name':'default', 'package_name':dotted_path(source)}
    
    # now lets call config_db from the __init__.py
    imps = Imports(module)
    imps.set('sqla_config', 'config_db')
    main = module.functions('main')[0]
    term = 'config.make_wsgi_app'
    make_app = main.blocks(term)[0]
    lines = make_app.lines
    # find occurrence of line in block
    index = -1
    found = False
    for i in range(len(lines)):
        if term in lines[i]:
            index = i
        if 'config_db' in lines[i]:
            found = True
            
    tok = token('config', True, main=main, module=module)
    if index != -1 and not found:
        lines.insert(index, 'config_db(config)')

@handler('setup_i18n', 'uml2fs', 'pyramid_semanticsgenerator', 'i18_egg')
def setup_i18n(self, source, target):
    tdir = read_target_node(source, target.target)
    init = tdir['__init__.py']
    imps = Imports(init)
    imps.set('pyramid.i18n', 'TranslationStringFactory')
    if not init.attributes('_'):
        att = Attribute(['_'], "TranslationStringFactory('%s')" % source.name)
        att.__name__ = str(att.uuid)
        init.insertafterimports(att)

bootstrap_templ = """
root=%s()
return root
"""

@handler('create_site_root', 'uml2fs', 'connectorgenerator', 'pyramid_siteroot')
def create_site_root(self, source, target):
    targetclass = read_target_node(source, target.target)
    module = targetclass.parent
    if not module.functions('bootstrap'):
        func = Function('bootstrap')
        func.insertlast(Block(bootstrap_templ % source.name))
        module.insertafter(func, targetclass)
    else:
        func = module.functions('bootstrap')[0]
    # mark the class because it has to be referenced by main
    token('site_root', True, site_root=source, klass=read_target_node(source, target.target), bootstrap=func)
