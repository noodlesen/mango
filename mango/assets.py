from flask_assets import Environment, Bundle

assets = Environment()

bundles = {


    # BASE PAGES ================================
 
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
        filters='cssmin'),

    'helper_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'css/main.css',
        output='gen/helper.css',
        filters='cssmin'),


    # USER AREA CSS =============================

    'favorites_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'geo/css/tipsflow.css',
        output='gen/favorites.css',
        filters='cssmin'),

    'my_tips_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'geo/css/tipsflow.css',
        output='gen/my_tips.css',
        filters='cssmin'),

    'messenger_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'social/css/messenger.css',
        output='gen/messenger.css',
        filters='cssmin'),

    'profile_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'social/css/profile.css',
        output='gen/profile.css',
        filters='cssmin'),

    'public_profile_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'social/css/public_profile.css',
        'geo/css/tipsflow.css',
        'geo/css/login_modal.css',
        output='gen/public_profile.css',
        filters='cssmin'),

    'user_events_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'social/css/user_events.css',
        output='gen/user_events.css',
        filters='cssmin'),


    # USER AREA JS =============================

    'favorites_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'lib/moment-with-locales.min.js',
        'geo/js/tipsflow.js',
        output='gen/favorites.js',
        filters='jsmin'),

    'my_tips_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'lib/moment-with-locales.min.js',
        'geo/js/tipsflow.js',
        output='gen/my_tips.js',
        filters='jsmin'),

    'messenger_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'lib/moment-with-locales.min.js',
        'social/js/messenger.js',
        output='gen/messenger.js',
        filters='jsmin'),

    'profile_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'social/js/profile.js',
        'lib/dmuploader.min.js',
        output='gen/profile.js',
        filters='jsmin'),

    'user_events_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'social/js/user_events.js',
        output='gen/user_events.js',
        filters='jsmin'),

    'public_profile_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'lib/moment-with-locales.min.js',
        'geo/js/tipsflow.js',
        'social/js/public_profile.js',
        output='gen/public_profile.js',
        filters='jsmin'),

    # PLACES =============================

    'place_css': Bundle(
        'css/base.css',
        'css/common.css',
        'css/ui.css',
        'geo/css/place.css',
        'geo/css/tipsflow.css',
        'geo/css/login_modal.css',
        output='gen/place.css',
        filters='cssmin'),

    'place_js': Bundle(
        'lib/vue.js',
        'js/common.js',
        'js/base.js',
        'lib/moment-with-locales.min.js',
        'lib/sharer.js',
        'geo/js/tipsflow.js',
        'geo/js/place.js',
        output='gen/place.js',
        filters='jsmin'),


}
 
assets.register(bundles)