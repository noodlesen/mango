from flask_assets import Environment, Bundle

assets = Environment()

bundles = {
 
    'root_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        output='gen/root.js',
        filters='jsmin'),

    'root_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'css/main.css',
        output='gen/root.css',
        filters='cssmin')
}
 
assets.register(bundles)