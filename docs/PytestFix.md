The `RuntimeError: Unable to build URLs outside an active request without 'SERVER_NAME' configured. Also configure 'APPLICATION_ROOT' and 'PREFERRED_URL_SCHEME' as needed.` indicates that Flask's URL generation (`url_for`) is failing in your test environment because the necessary configuration for building URLs is missing.

In a testing environment, Flask needs to know the `SERVER_NAME` and `PREFERRED_URL_SCHEME` to correctly generate URLs, even if no actual server is running. This is crucial for functions like `url_for` to work properly.

To fix this, you should add these configurations to your Flask application's testing configuration. A common place to do this is in your `conftest.py` file, within the `app` fixture, or in your `src.config.TestingConfig` if you have one.

**Option 1: Modify `conftest.py` (Recommended for testing)**

If you are creating your app instance directly in `conftest.py` (as seen in your previous `conftest.py` file), you can set these configurations directly on the `app` object:

```python
# tests/conftest.py

import pytest
from src.main import create_app
from src.extensions import db


@pytest.fixture(scope="module")
def app():
    # Instantiate Flask app with testing config
    app = create_app("src.config.TestingConfig")

    # Add SERVER_NAME and PREFERRED_URL_SCHEME for URL generation in tests
    app.config["SERVER_NAME"] = "localhost.localdomain:5000"  # Or any suitable test domain
    app.config["PREFERRED_URL_SCHEME"] = "http"

    # Ensure SQLAlchemy is initialized with this app, but only once
    with app.app_context():
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            db.init_app(app)

    return app

# ... rest of your conftest.py ...
```

**Option 2: Modify `src.config.TestingConfig` (If you have a dedicated testing config)**

If you have a separate configuration class for testing (e.g., `src.config.TestingConfig`), you can add these settings there:

```python
# src/config.py (or wherever your config classes are defined)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = "localhost.localdomain:5000"  # Or any suitable test domain
    PREFERRED_URL_SCHEME = "http"
    # ... other testing configurations ...
```

**Explanation:**

*   `app.config["SERVER_NAME"]`: This tells Flask what the server's hostname and port are. Even in tests where no actual server is running, `url_for` needs this to construct absolute URLs. You can use any valid domain, `localhost.localdomain:5000` is a common choice for testing.
*   `app.config["PREFERRED_URL_SCHEME"]`: This specifies the default URL scheme (e.g., `http` or `https`) to use when generating URLs. For local testing, `http` is usually sufficient.

By adding these configurations, Flask will have the necessary context to generate URLs within your test environment, resolving the `RuntimeError`.

