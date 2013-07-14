### flask 资源自动编译插件  
根据给出的定义，把源文件编译至指定文件夹；并自动清理没用了的编译结果  
部分灵感来自于 flask_cake 插件

---

#### 使用范例

    :::python
    from flask.ext import assets_compile
    manager = assets_compile.DefinitionManager(app)
    manager.register(assets_compile.example_definitions)

    # 为 blueprint 定义资源
    manager.register(some_definitions, blueprint_obj)

---

#### "资源定义(asset_definition)"的格式

    :::python
    asset_definitions = [
        (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ]
    # source_dir 和 compiled_dir 是可选的，他们的值都是针对 app/blueprint.root_path 的相对路径

一个 asset_definitions 里可以定义多种资源  
compile_cmd 的格式，以及资源定义的范例，请参考源代码 flask_assets_compile.py 里的 example_defintions

---

#### Debug 模式

DefinitionManager 初始化时，会检查传递进来的 app 对象的 config
如果 debug=True 则启用 debug 模式  
此时，客户端每发起一个 request ，asset_compiler 都会检查一次源文件， 并在发现变动时进行编译
否则，它只会在应用启动时检查一次

---

#### 其他

1. 此插件会递归进入 source_dir 的子文件夹寻找可编译的文件  
2. 源文件删除后，对应的已编译文件、文件夹也会被删除  
3. 未来准备支持用函数代替 compile_cmd

