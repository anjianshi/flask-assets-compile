# -*- coding: utf-8  -*-

"""
不做任何关于文件夹的处理。
包括：
    不递归进入文件夹进行编译
    对于 compiled_dir ，只清理其中的文件，不清理其中的文件夹
"""

import os
import subprocess

_default_definition = [
    # (source_dir, compiled_dir, compiled_ext, compile_cmd)
    ('coffee', 'compiled', 'js', 'coffee --bare --output {compiled_dir} --compile {source}'),
    ('less', 'compiled', 'css', 'lessc --yui-compress {source} {compiled}')
]

_static_dir = None


def compile(app, asset_define=_default_definition):
    global _static_dir
    # 若不加这句，通过 pycharm 启动应用时无法访问 static 文件夹
    _static_dir = os.path.join(app.root_path, app.static_folder)
    for definition in asset_define:
        _Compiler(*definition)


class _Compiler(object):
    def __init__(self, source_dir, compiled_dir, compiled_ext, compile_cmd):
        self.source_dir = os.path.join(_static_dir, source_dir)
        self.compile_cmd = compile_cmd
        self.compiled_dir = os.path.join(_static_dir, compiled_dir)
        if compiled_ext.find('.') is not 0:
            compiled_ext = '.' + compiled_ext
        self.compiled_ext = compiled_ext
        self.marked_assets = []

        self.traverse_assets()
        self.clean_compiled_dir()

    def traverse_assets(self):
        for source in os.listdir(self.source_dir):
            if os.path.isfile(os.path.join(self.source_dir, source)):
                self.marked_assets.append(self.pure_name(source))
                paths = self.parse_paths(source)
                if self.need_compile(paths):
                    self.compile(paths)

    def pure_name(self, source):
        return source[:source.index('.')]

    def parse_paths(self, source):
        return {
            'source': os.path.join(self.source_dir, source),
            'compiled': os.path.join(self.compiled_dir, self.pure_name(source))+self.compiled_ext
        }

    def need_compile(self, paths):
        return (not os.path.isfile(paths['compiled'])) \
            or self.get_mtime(paths['source']) > self.get_mtime(paths['compiled'])

    def get_mtime(self, path):
        return os.stat(path).st_mtime

    def compile(self, paths):
        paths['compiled_dir'] = self.compiled_dir
        cmd = self.compile_cmd.format(**paths)

        with open(os.devnull, 'w') as devnull:
            p = subprocess.Popen(cmd, shell=True, stdout=devnull)
            p.wait()

    def clean_compiled_dir(self):
        """清理应该被删除的旧asset"""
        if os.path.isdir(self.compiled_dir):
            for compiled in os.listdir(self.compiled_dir):
                compiled_path = os.path.join(self.compiled_dir, compiled)
                if os.path.isfile(compiled_path):
                    name, ext = os.path.splitext(compiled)
                    if ext == self.compiled_ext and name not in self.marked_assets:
                        os.remove(compiled_path)





