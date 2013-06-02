### flask 资源自动编译插件  
根据给出的定义，把源文件编译至指定文件夹；并自动清理没用了的编译结果

---

#### 使用范例

    :::python
    import assets_compiler

    if app.config['DEBUG']:
        @app.before_request
        def asset_before_request():
            assets_compiler.execute(app)
    elif __name__ == '__main__':
        assets_compiler.execute(app)

此时因为没有传入任何"定义"，系统会使用默认的"定义"：把 static/coffee 和 static/less 下的文件编译至 static/compiled 里
(需要 nodejs, coffee-script, less)

---

#### "定义"的格式

    :::python
    definition = [
        (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ]
    # source_dir 和 compiled_dir 是可选的

    asset_compiler.execute(app, definition)

---

你也可以手动调用 `asset_compiler.Compiler(...)` 完成同样的任务，只不过这样一次只能编译一种资源

    :::python
    asset_compiler.Compiler(app, source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    # 同样，最后两个参数可选

---

asset_compiler 会递归进入 source_dir 的子文件夹寻找可编译的文件  
源文件删除后，对应的已编译文件、文件夹也会被删除  
未来准备支持用函数代替 compile_cmd
