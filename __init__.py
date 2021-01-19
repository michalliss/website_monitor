from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_apscheduler import APScheduler

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

db = SQLAlchemy()
scheduler = APScheduler()


def create_app():
    app = Flask(__name__, static_url_path='/static')

    app.config['SECRET_KEY'] = 'JeZyKi_SkRyPtOwE'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.metadata.clear()
    db.init_app(app)

    from .models import Website
    from .models import WebsiteStatus
    scheduler.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .controllers.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .controllers.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .controllers.websites import websites as websites_blueprint
    app.register_blueprint(websites_blueprint)

    # Set this decorator when running in development mode to prevent loading tasks twice
    @app.before_first_request
    def reset_attacks():
        websites = Website.query.all()
        for website in websites:
            website.attack = False
            db.session.add(website)
        db.session.commit()

    scheduler.start()

    # Set this decorator when running in development mode to prevent loading tasks twice
    @app.before_first_request
    def load_tasks():
        from .utils import tasks

    # Uncomment to recreate database
    # db.create_all(app=app)
    return app
