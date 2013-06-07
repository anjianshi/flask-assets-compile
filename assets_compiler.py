# -*- coding: utf-8  -*-

import os
import subprocess

_default_definition = [
    # (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ('coffee', 'js', 'coffee --bare --output {compiled_dir} --compile {source}', 'static/coffee', 'static/compiled'),
    ('less', 'css', 'lessc --yui-compress {source} {compiled}', 'static/less', 'static/compiled',)
]


def register(app, asset_definition=_default_definition):
    def execute():
        for definition in asset_definition:
            _Compiler(app.root_path, *definition)
            
    if app.config['DEBUG']:
        @app.before_request
        def compile_asset_before_request():
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
    if os.path.isdir(path):
        for item in os.listdir(path):
            item = path + '/' + item
            if os.path.isfile(item):
                callback(item)
            else:
                _dir_walk(item, callback)
