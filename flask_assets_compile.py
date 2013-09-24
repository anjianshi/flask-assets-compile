# -*- coding: utf-8  -*-

import os
import subprocess

__version__ = 0.1


class CmdCompiler(object):
    def __init__(self, cmd_pattern, source_ext, compiled_ext):
        """cmd_pattern 中必须包含一个占位符，在执行编译时，它会被替换为源文件的绝对路径"""
        self.cmd_pattern = cmd_pattern
        self.source_ext = source_ext
        self.compiled_ext = compiled_ext

    def __call__(self, source_path):
        cmd = self.cmd_pattern.format(source_path)
        return subprocess.check_output(cmd, shell=True)

compilers = {
    'coffee': CmdCompiler('coffee --bare --print --compile {}', 'coffee', 'js'),
    'less': CmdCompiler('lessc --yui-compress {}', 'less', 'css')
}

example_definitions = [
    # (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ('static/coffee', 'static/compiled', compilers['coffee']),
    ('static/less', 'static/compiled', compilers['less'])
]


class _Execute(object):
    def __init__(self, root_path, source_dir, compiled_dir, compiler):
        self.source_dir = root_path + '/' + source_dir
        self.compiled_dir = root_path + '/' + compiled_dir
        self.source_ext = _fix_ext(compiler.source_ext)
        self.compiled_ext = _fix_ext(compiler.compiled_ext)

        sources = self.get_sources()
        self.clean_compiled()

        for source in sources:
            compiled_path = self.path_map(source)
            if not os.path.isfile(compiled_path):
                the_dir = os.path.dirname(compiled_path)
                if not os.path.exists(the_dir):
                    os.makedirs(the_dir)

                with open(compiled_path, 'w') as compiled:
                    compiled.write(compiler(source))

    def get_sources(self):
        sources = []
        _dir_walk(self.source_dir,
                  lambda path: (os.path.splitext(path)[1] == self.source_ext) and sources.append(path))
        return sources

    def path_map(self, source=None, compiled=None):
        """给出 source 与 compiled 中的任意一项，返回与之对应的另一项"""
        if source is not None:
            return source.replace(self.source_dir, self.compiled_dir).replace(self.source_ext, self.compiled_ext)
        elif compiled is not None:
            return compiled.replace(self.compiled_dir, self.source_dir).replace(self.compiled_ext, self.source_ext)

    def clean_compiled(self):
        def handler(compiled):
            if os.path.splitext(compiled)[1] == self.compiled_ext:
                source = self.path_map(compiled=compiled)
                if not os.path.isfile(source):
                    # 对应的 source 不存在，将 compiled 删除
                    # 此时，若所在文件夹为空，把文件夹也删除
                    os.remove(compiled)

                    the_dir = os.path.split(compiled)[0]
                    if not os.listdir(the_dir):
                        os.rmdir(the_dir)
                elif os.stat(source).st_mtime > os.stat(compiled).st_mtime:
                    # source 更新过, 所以 compiled 文件已过时
                    # 这类文件即使不删除，也会在编译源文件时自动把它们替换掉。
                    # 但那样一旦源文件编译错误，已经过时的编译结果就不会被删除，继续生效。
                    # 最终可能导致程序员误判情况，在错误的方向上浪费时间
                    os.remove(compiled)
        _dir_walk(self.compiled_dir, handler)


class DefinitionManager(object):
    def __init__(self, app=None, default_definitions=example_definitions):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None
            self.debug = False

        self.default_definitions = default_definitions

    def init_app(self, app):
        self.app = app
        self.debug = app.config['DEBUG']

    def register(self, definitions=None, app_or_blueprint=None):
        if definitions is None:
            definitions = self.default_definitions
            
        if not isinstance(definitions, list):
            definitions = [definitions]

        if app_or_blueprint is None:
            app_or_blueprint = self.app

        def execute():
            for definition in definitions:
                _Execute(app_or_blueprint.root_path, *definition)

        if self.debug is True:
            app_or_blueprint.before_request(execute)
        else:
            execute()


class _Compiler(object):
    def __init__(self, root_path, source_ext, compiled_ext, compile_cmd, source_dir='static', compiled_dir='static/compiled'):        
        self.source_ext = _fix_ext(source_ext)
        self.compiled_ext = _fix_ext(compiled_ext)
        self.compile_cmd = compile_cmd
        self.source_dir = root_path + '/' + source_dir
        self.compiled_dir = root_path + '/' + compiled_dir

        self.source_list = self.get_source_list()
        self.clean_compiled()
        for source in self.source_list:
            if not os.path.isfile(self.path_map(source)):
                self.compile(source)

    def get_source_list(self):
        sources = []
        _dir_walk(self.source_dir,
                  lambda path: (os.path.splitext(path)[1] == self.source_ext) and sources.append(path))
        return sources

    def path_map(self, source=None, compiled=None):
        """
            给出 source 与 compiled 中的任意一项，返回与之对应的另一项
        """
        if source is not None:
            return source.replace(self.source_dir, self.compiled_dir).replace(self.source_ext, self.compiled_ext)
        elif compiled is not None:
            return compiled.replace(self.compiled_dir, self.source_dir).replace(self.compiled_ext, self.source_ext)

    def clean_compiled(self):
        """
            删除没用的 compiled_file，包括：
                1. 对应的source已经不存在
                    (此时，如果删除后 compiled_file 所在的文件夹为空，会连带把文件夹也删除)
                2. source 更新过, compiled 文件已过时
                    这类文件即使不删除，也会在编译源文件时自动把它们替换掉。
                    但那样一旦源文件编译错误，已经过时的编译结果就不会被删除，继续生效。
                    最终可能导致程序员误判情况，在错误的方向上浪费时间
            最后，只保留 source 不需要编译了的 compiled 
        """
        def handler(compiled):
            if os.path.splitext(compiled)[1] == self.compiled_ext:
                source = self.path_map(compiled=compiled)
                if not os.path.isfile(source):
                    os.remove(compiled)

                    the_dir = os.path.split(compiled)[0]
                    if not os.listdir(the_dir):
                        os.rmdir(the_dir)
                elif os.stat(source).st_mtime > os.stat(compiled).st_mtime:
                    os.remove(compiled)
        _dir_walk(self.compiled_dir, handler)

    def compile(self, source):
        compiled = self.path_map(source)
        env = {
            'source': source,
            'compiled': compiled,
            'compiled_dir': os.path.split(compiled)[0]
        }
        cmd = self.compile_cmd.format(**env)
        with open(os.devnull, 'w') as devnull:
            p = subprocess.Popen(cmd, shell=True, stdout=devnull)
            p.wait()


def _fix_ext(ext):
    """给没有前缀'.'的文件扩展名加上'.'"""
    return (ext.find('.') is 0) and ext or '.' + ext


def _dir_walk(path, callback):
    """遍历给出的文件夹及其子文件夹，把遇到的每个文件传给 callback 处理"""
    for dirpath, dirs, files in os.walk(path):
        for item in files:
            callback(dirpath + '/' + item)
        for item in dirs:
            _dir_walk(dirpath + '/' + item, callback)