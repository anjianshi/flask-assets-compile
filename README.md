用于 flask 的资源自动编译插件

Example:  
    :::python
    import assets_compile

    if app.config['DEBUG']:
        @app.before_request
        def asset_before_request():
            assets_compile.compile(app)
    elif __name__ == '__main__':
        assets_compile.compile(app)

assets_compile 默认会把 static/coffee 和 static/less 下的文件编译到 static/compiled 文件夹里。（需要你的机器安装有 nodejs, coffee-script 和 less)  
可以通过给 compile() 函数传入第二个参数 asset_define 更改其行为

asset_define 的格式如下：
    :::python
    [
        (source_dir, compiled_dir, compiled_ext, compile_cmd)
    ]
例如默认的 asset_define：
    :::python
    assets_compile.compile(app, [
        ('coffee', 'compiled', 'js', 'coffee --bare --output {compiled_dir} --compile {source}'),
    ('less', 'compiled', 'css', 'lessc --yui-compress {source} {compiled}')
    ])

目前不支持递归进入子目录进行编译，未来预计会支持
另外，未来还准备支持用 python 函数做 compile_cmd
