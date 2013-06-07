### flask 资源自动编译插件  
根据给出的定义，把源文件编译至指定文件夹；并自动清理没用了的编译结果  
部分灵感来自于 flask_cake 插件

---

#### 使用范例

    :::python
    import assets_compiler
    assets_compiler.register(app, asset_definition)

---

#### "资源定义(asset_definition)"的格式

    :::python
    asset_definition = [
        (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
    ]
    # source_dir 和 compiled_dir 是可选的

一个 asset_definition 里可以定义多种资源  
compile_cmd 的格式，以及资源定义的范例，请参考源代码里的 _default_definition

---

#### Debug 模式

可以给 register 函数传递 debug=True 来启用 debug 模式  
此时，客户端每发起一个 request ，asset_compiler 都会检查一次源文件（并在发现变动时进行编译）  
否则，它只会在应用启动时检查一次

对于 Flask app（即：不是一个 Blueprint），在没有给出 debug 参数时，asset_compiler 会自动检查 app.config['DEBUG'] 来确定是否启用 debug 模式  
Blueprint 则只能手动启用 debug 模式

---

#### 其他

1. asset_compiler 会递归进入 source_dir 的子文件夹寻找可编译的文件  
2. 源文件删除后，对应的已编译文件、文件夹也会被删除  
3. 未来准备支持用函数代替 compile_cmd

