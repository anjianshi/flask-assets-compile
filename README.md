### flask 资源自动编译插件  
根据给出的定义，把源文件编译至指定文件夹；并自动清理没用了的编译结果  
部分灵感来自于 flask_cake 插件

---

#### 使用范例

##### 一

    :::python
    from flask.ext import assets_compile
    manager = assets_compile.DefinitionManager(app)
    manager.register(some_definitions)

    # 为 blueprint 定义资源
    manager.register(some_definitions, blueprint_obj)

##### 二

    :::python
    # 也可以指定一个 default_definitions ，让 app 和 blueprint 共用同一个 definitions。（当然，输入和输出的目录会根据他们各自的 root_path 分别计算）
    manager = assets_compile.DefinitionManager(app, the_default_definitions)
    # for app
    manager.register()
    # for blueprint
    manager.register(app_or_blueprint=blueprint)

##### 三

    :::python
    # 在没指定 default_defintions 时，会把 assets_compile.example_definitions 当做 default_definitions
    # example_definitions 包含了对 CoffeeScript 和 LESS 的编译指令，依赖 nodejs 的 coffee-script 和 less 包
    manager = assets_compile.DefinitionManager(app)
    # for app
    manager.register()
    # for blueprint
    manager.register(app_or_blueprint=blueprint)

---

#### "资源定义(asset_definition)"的格式

    :::python
    asset_definitions = [
        (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ]
    # source_dir 和 compiled_dir 是可选的，他们的值都是针对 app/blueprint.root_path（注意，不是 static_folder） 的相对路径

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

