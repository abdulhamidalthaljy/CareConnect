import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect

# Central extension objects used across the app
db = SQLAlchemy()
login_manager = LoginManager()

# Use gevent in production (Render), threading locally/tests
# Try to import gevent to see if it's available
try:
    import gevent
    _async_mode = 'gevent'
except ImportError:
    _async_mode = 'threading'

# Override: If running pytest, always use threading
if os.environ.get('PYTEST_CURRENT_TEST') or os.environ.get('FLASK_TESTING'):
    _async_mode = 'threading'

socketio = SocketIO(async_mode=_async_mode, cors_allowed_origins='*')
csrf = CSRFProtect()

# Recommended: redirect anonymous users to the login view
login_manager.login_view = 'auth.login'