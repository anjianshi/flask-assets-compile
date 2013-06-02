# -*- coding: utf-8  -*-

import os
import subprocess

_default_definition = [
    # (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ('coffee', 'js', 'coffee --bare --output {compiled_dir} --compile {source}', 'static/coffee', 'static/compiled'),
    ('less', 'css', 'lessc --yui-compress {source} {compiled}', 'static/less', 'static/compiled',)
]


def execute(app, asset_definition=_default_definition):
    for definition in asset_definition:
        Compiler(app, *definition)


class Compiler(object):
    def __init__(self, app, source_ext, compiled_ext, compile_cmd, source_dir='static', compiled_dir='static/compiled'):
        root_path = app.root_path
        self.source_ext = fix_ext(source_ext)
        self.compiled_ext = fix_ext(compiled_ext)
        self.compile_cmd = compile_cmd
        self.source_dir = root_path + '/' + source_dir
        self.compiled_dir = root_path + '/' + compiled_dir

        self.source_list = self.get_source_list()
        self.clean_compiled()
        for source in self.source_list:
            self.compile(source)

    def get_source_list(self):
        sources = []
        dir_walk(self.source_dir,
                 lambda path: (os.path.splitext(path)[1] == self.source_ext) and sources.append(path))
        return sources

    def clean_compiled(self):
        """
            删除没用的 compiled_file（例如对应的source已经不存在）
            如果删除后 compiled_file 所在的文件夹为空，会连带把文件夹也删除(这个功能要测试一下能不能用)
        """
        def handler(path):
            if os.path.splitext(path)[1] == self.compiled_ext:
                source = path.replace(self.compiled_dir, self.source_dir).replace(self.compiled_ext, self.source_ext)
                if not os.path.isfile(source):
                    os.remove(path)

                    the_dir = os.path.split(path)[0]
                    if not os.listdir(the_dir):
                        os.rmdir(the_dir)
        dir_walk(self.compiled_dir, handler)

    def need_compile(self, source, compiled):
        return not os.path.isfile(compiled) or get_mtime(source) > get_mtime(compiled)

    def compile(self, source):
        compiled = source.replace(self.source_dir, self.compiled_dir).replace(self.source_ext, self.compiled_ext)
        if self.need_compile(source, compiled):
            env = {
                'source': source,
                'compiled': compiled,
                'compiled_dir': os.path.split(compiled)[0]
            }
            cmd = self.compile_cmd.format(**env)
            with open(os.devnull, 'w') as devnull:
                p = subprocess.Popen(cmd, shell=True, stdout=devnull)
                p.wait()


def fix_ext(ext):
    """给没有前缀'.'的文件扩展名加上'.'"""
    return (ext.find('.') is 0) and ext or '.' + ext


def dir_walk(path, callback):
    """遍历给出的文件夹及其子文件夹，把遇到的每个文件传给 callback 处理"""
    if os.path.isdir(path):
        for item in os.listdir(path):
            item = path + '/' + item
            if os.path.isfile(item):
                callback(item)
            else:
                dir_walk(item, callback)


def get_mtime(path):
    return os.stat(path).st_mtime