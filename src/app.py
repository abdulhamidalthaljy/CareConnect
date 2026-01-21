from flask import Flask, render_template
from src.config import Config
from src.extensions import db, login_manager, socketio, csrf
from src.views.main import main as main_blueprint
from src.views.auth import auth as auth_blueprint
from src.views.doctor import doctor as doctor_blueprint
from src.views.appointments import appointments as appointments_blueprint
from src.views.chat import chat as chat_blueprint


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # allow test overrides (e.g., in-memory SQLite)
    if test_config:
        app.config.update(test_config)

    # initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    # initialize CSRF protection
    csrf.init_app(app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(doctor_blueprint)
    app.register_blueprint(appointments_blueprint)
    app.register_blueprint(chat_blueprint)

    # Friendly 403 handler that renders a template
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    # Create database tables on startup
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=app.config.get('DEBUG', False))