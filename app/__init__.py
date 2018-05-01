#-*- coding=utf-8 -*-
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from config import config, basedir
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail
from datetime import timedelta
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'None'
mail = Mail()


def create_app(config_name):
    app = Flask(__name__, static_folder=basedir+'/static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.update(
        MAIL_SERVER='smtp.qq.com',
        MAIL_PROT=465,
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=True,
        MAIL_USERNAME="1468767640@qq.com",
        MAIL_PASSWORD="uhieluellzqwhaea",
        MAIL_DEBUG=True
    )

    login_manager.init_app(app)
    login_manager.remember_cookie_duration = timedelta(days=1000)



    db.init_app(app)
    mail.init_app(app)


    from .gencode import gencode_blueprint
    app.register_blueprint(gencode_blueprint, url_prefix='/')

    from .accuchek import accuchek_blueprint
    app.register_blueprint(accuchek_blueprint, url_prefix='/')

    from .bed import bed_blueprint
    app.register_blueprint(bed_blueprint, url_prefix='/')

    from .operator import operator_blueprint
    app.register_blueprint(operator_blueprint, url_prefix='/')

    from .data import data_blueprint
    app.register_blueprint(data_blueprint, url_prefix='/')

    from .patient import patient_blueprint
    app.register_blueprint(patient_blueprint, url_prefix='/')

    from .error import error_blueprint
    app.register_blueprint(error_blueprint, url_prefix='/')

    CORS(app, supports_credentials=True)

    return app
