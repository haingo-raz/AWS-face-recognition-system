from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'HHHHHH'

    #Blueprint views
    from .views import views

    #Register blueprints
    app.register_blueprint(views, url_prefix='/')

    return app