# -*- coding: utf-8  -*-

import os
import subprocess

__version__ = 0.1


"""

因 Flask 本身就能在 assets 文件更新时自动重启，所以不必再考虑 debug 模式了。
只要一直在应用启动时检查/编译一次就行。



definition 中，不再包含具体的 command，而是给出一个用于执行编译的函数(compiler)，这个函数接收一个参数：source_path，返回编译结果。
模块中，已经预定义了一些常用的 compiler，并给出了几个 helper class，辅助用户创建自己的 compiler

另外，原本由 command 直接把编译结果输出到文件的行为方式也发生了改变，现在必须把编译结果返回给模块，再由模块来输出到文件
这是为了便于在个别情况下，对编译结果进行二次处理，例如合并
同时也为未来支持嵌套定义提供基础
"""

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

# todo: 没考虑到顺序问题。 combine 不应加到 asset_compile 里，还是应该分离出去
class _Execute(object):
    def __init__(self, root_path, source_dir, compiled_dir, compiler, combined_name=None):
        self.source_dir = root_path + '/' + source_dir
        self.compiled_dir = root_path + '/' + compiled_dir
        self.source_ext = _fix_ext(compiler.source_ext)
        self.compiled_ext = _fix_ext(compiler.compiled_ext)
        self.combined_name = combined_name

        sources = self.get_sources()
        self.clean_compiled()

        if combined_name:
            combined_path = self.compiled_dir + '/' + combined_name + self.compiled_ext
            if not os.path.isfile(combined_path) and len(sources) > 0:
                contents = {}
                for source in sources:
                    contents[os.path.splitext(source)[0]] = compiler(source)

                if not os.path.exists(self.compiled_dir):
                    os.makedirs(self.compiled_dir)

                with open(combined_path, 'w') as combined:
                    combined.write("\n\n\n".join(contents.values()))

                #with open(self.compiled_dir + '/' + combined_name + '.combine_meta', 'w') as meta:
                #    meta.write("\n".join(contents.keys()))
        else:
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
        if self.combined_name is None:
            def handler(compiled):
                if os.path.splitext(compiled)[1] == self.compiled_ext:
                    source = self.path_map(compiled=compiled)
                    if not os.path.isfile(source):
                        # 对应的 source 不存在，将 compiled 删除
                        # 此时，若所在文件夹为空，把文件夹也删除
                        _rm(compiled, True)
                    elif os.stat(source).st_mtime > os.stat(compiled).st_mtime:
                        # source 更新过, 所以 compiled 文件已过时
                        # 这类文件即使不删除，也会在编译源文件时自动把它们替换掉。
                        # 但那样一旦源文件编译错误，已经过时的编译结果就不会被删除，继续生效。
                        # 最终可能导致程序员误判情况，在错误的方向上浪费时间
                        _rm(compiled)
            _dir_walk(self.compiled_dir, handler)

        else:
            combined_path = self.compiled_dir + '/' + self.combined_name + self.compiled_ext
            meta_path = self.compiled_dir + '/' + self.combined_name + '.combine_meta'

            # 遍历 compiled 文件夹，把名称不等于 combine_name 的都删除
            _dir_walk(self.compiled_dir, lambda compiled:
                (compiled != combined_path and os.path.splitext(compiled)[1] == self.compiled_ext) and os.remove(compiled)
            )

            # 若 combined 和 meta 没有同时存在，把存在的那一方删掉。若都不存在，直接返回，不必再进行操作
            combined_exists = os.path.isfile(combined_path)
            meta_exists = os.path.isfile(meta_path)
            if not combined_exists and not meta_exists:
                return
            elif combined_exists and not meta_exists:
                _rm(combined_path)
                return
            elif meta_exists and not combined_exists:
                _rm(meta_exists)
                return

            # 若 source 文件夹中的文件与 combine_meta 记录的不一致，或者某个文件的 last_modified 高于 combined，将 combined(以及 meta) 删除
            sources = self.get_sources()
            source_set = set([os.path.splitext(os.path.basename(path))[0] for path in sources])
            with open(meta_path) as meta:
                combined_source_set = set(meta.readall().split("\n"))
            if source_set != combined_source_set:
                _rm(combined_path)
                _rm(meta_path, True)
            else:
                for source in sources:
                    if os.stat(source).st_mtime > os.stat(combined_path).st_mtime:
                        os.remove(combined_path)
                        os.remove(meta_path)
                        break


example_definitions = [
    # (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ('static/coffee', 'static/compiled', compilers['coffee']),
    ('static/less', 'static/compiled', compilers['less'])
]



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


def _rm(filepath, try_rm_path=False):
    """删除指定文件。若 try_rm_path 为 True，会在其所在文件夹为空时将文件夹也删除"""
    os.remove(filepath)

    if try_rm_path:
        the_dir = os.path.split(filepath)[0]
        if not os.listdir(the_dir):
            os.rmdir(the_dir)

	