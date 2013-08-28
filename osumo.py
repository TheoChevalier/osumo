import json
import urllib
import os

from flask import (
    Flask,
    render_template,
    make_response,
    abort,
    request,
    send_file
)
from flask.ext.appcache import Appcache
from flask.ext.assets import Environment, Bundle

import requests

# Create the app
app = Flask(__name__)
app.config.from_pyfile("settings.py")
app.config.from_pyfile("settings_local.py", silent=True)

# Getting the supported languages from SUMO
LANGUAGES = requests.get((app.config['SUMO_URL'] +
                         'offline/get-languages')).json()
LANGUAGES = json.dumps(LANGUAGES['languages'])

# Sets up the assets
assets = Environment(app)
assets.debug = app.debug

css = Bundle(
    'css/develop/gaia.css',
    'css/develop/doc.css',
    'css/develop/installer.css',
    'css/develop/nav.css',
    'css/develop/app.css',
    filters='cssmin',
    output='css/app.min.css'
)
assets.register('css_all', css)

scripts = ['js/develop/app.js']
for root, subdir, fnames in os.walk('static/js/develop'):
    for filename in fnames:
        if filename.endswith('.js') and filename != 'app.js':
            # get rid of te 'static/'
            scripts.append(os.path.join(root, filename)[7:])

js = Bundle(*scripts, filters='uglifyjs', output='js/app.min.js')
assets.register('js_all', js)

# Sets up the angular partials
# TODO!!
PARTIALS = ""
if not app.debug:
    pass

# Sets up Appcache
appcache = Appcache(app)
if app.debug:
    appcache.add_excluded_urls('/static/js/app.min.js',
                               '/static/css/app.min.css')
else:
    appcache.add_excluded_urls('/static/js/develop')
    appcache.add_excluded_urls('/static/js/css')
    appcache.add_excluded_urls('/static/partials')

appcache.add_excluded_urls('/static/.webassets-cache')
appcache.add_folder('static')
appcache.add_urls('/meta.js', '/')


@app.before_request
def before_request():
    app.jinja_env.globals['partials'] = PARTIALS


@app.route('/manifest.webapp')
def manifest_webapp():
    return send_file('manifest.webapp',
                     mimetype='application/x-web-app-manifest+json')


@app.route('/images')
def images():
    if 'url' not in request.args:
        return abort(400)

    target = 'https://support.cdn.mozilla.net/' + request.args['url']
    response = requests.get(target)
    if response.status_code == 200:
        imgdata = ('data:image/png;base64,' +
                   urllib.quote(response.content.encode('base64')))
        response = make_response(imgdata)
        response.mimetype = 'text/plain'
        return response
    else:
        return abort(response.status_code)


@app.route('/meta.js')
def meta_js():
    context = {
        'COMMIT_SHA': app.config['COMMIT_SHA'],
        'APPCACHE_HASH': appcache.hash()[0],
        'BASE_URL': app.config['BASE_URL'],
        'SUMO_URL': app.config['SUMO_URL'],
        'LANGUAGES': LANGUAGES
    }
    response = make_response(render_template('meta.js', **context))
    response.mimetype = 'application/javascript'
    return response


# Catch all URL for HTML push state
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def main(path):
    return render_template('app.html')
