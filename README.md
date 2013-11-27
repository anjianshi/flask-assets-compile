### Deprecated
please use Flask-Assets or Grunt instead

### document is out-of-date


### Flask assets auto compile extension
According to the definitions given，compile assets to specified folder; and clean up old, useless compile result.  
some idea was from [Flask-Cake](https://github.com/rsenk330/Flask-Cake)

---

#### Examples

##### No.1
```python
from flask.ext import assets_compile
manager = assets_compile.DefinitionManager(app)
manager.register(some_definitions)

# define assets for blueprint
manager.register(some_definitions, blueprint_obj)
```

##### No.2
```python
# you can define a default_definitions, then app and blueprint can use the same definitions.(of course, input and output directory'path will determined by their own root_path)
manager = assets_compile.DefinitionManager(app, the_default_definitions)
# for app
manager.register()
# for blueprint
manager.register(app_or_blueprint=blueprint)
```

##### No.3
```python
# if there's not a default_definitions, the extension well use assets_compile.example_definitions by default.
# the example_definitions include directives to compile coffeeScript and LESS.
# these directives depend coffee-script and less package in nodejs
manager = assets_compile.DefinitionManager(app)
# for app
manager.register()
# for blueprint
manager.register(app_or_blueprint=blueprint)
```

---

#### the format of asset_definition

```python

asset_definitions = [
    (source_ext, compiled_ext, compile_cmd, source_dir, compiled_dir)
]
# source_dir and compiled_dir are optional，their value are both relative path to app/blueprint.root_path (notice: it's root_path, instead of static_folder)
```

---

### Debug mode

When `DefinitionManager` is initialized, it will check `config` property of the app object user passed.  
If debug=True, turn on debug mode. Then, everytime client sent a request, the extension have to check about asset sources, and compile assets that has changed.  
Otherwise, it only checked once when the application starts  

---

### Other

1. this extension will find assets in source_dir recursively 
2. when source is deleted, the compiled asset and directory will be delete to
3. sorry, my english is not very well. translate the docment into this, I have tried my best. thanks Google.
