# tests/conftest.py

import pytest
import sys
import os

# Ensure project root is on sys.path so tests can import `src` when pytest
# is executed from different working directories (e.g., `src/`). This makes
# test discovery & imports more robust in local environments.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.app import create_app

@pytest.fixture
def app():
    # Provide a test-configured Flask app for all tests to reuse. Using a
    # single app instance avoids registering multiple apps with the
    # Flask-SQLAlchemy extension during the test run (which can cause
    # engine/registration issues across fixtures).
    test_config = {
        'TESTING': True,
        # Use a file-based SQLite DB for tests to avoid in-memory connection
        # isolation issues between different SQLAlchemy engines.
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
        # Disable CSRF in tests so test clients can POST without tokens
        'WTF_CSRF_ENABLED': False
    }
    app = create_app(test_config=test_config)
    # create DB schema for tests and ensure it's cleaned up afterwards
    from src.extensions import db
    # Ensure the db extension is initialized for this app (defensive: call init_app again)
    try:
        db.init_app(app)
    except Exception:
        # init_app may have been called already in create_app; ignore errors
        pass
    with app.app_context():
        # quick sanity check: the app should be registered with the SQLAlchemy instance
        try:
            registered = app in getattr(db, '_app_engines', {})
        except Exception:
            registered = False
        # proceed to create_all regardless; if registration still fails, tests will show the error
        db.create_all()
    yield app
    # teardown: drop DB and cleanup test artifacts (only when using test.db)
    with app.app_context():
        db.session.remove()
        db.drop_all()
    # remove the test sqlite file and any test uploads
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri and db_uri.endswith('test.db'):
        test_db_path = os.path.join(ROOT, 'test.db')
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
        except Exception:
            pass
        # remove uploads folder created by tests in src/uploads
        upload_folder = app.config.get('UPLOAD_FOLDER')
        try:
            if upload_folder and os.path.exists(upload_folder):
                # remove user subfolders only
                for entry in os.listdir(upload_folder):
                    full = os.path.join(upload_folder, entry)
                    if os.path.isdir(full):
                        # remove files inside
                        for f in os.listdir(full):
                            try:
                                os.remove(os.path.join(full, f))
                            except Exception:
                                pass
                        try:
                            os.rmdir(full)
                        except Exception:
                            pass
        except Exception:
            pass

@pytest.fixture
def client(app):
    return app.test_client()