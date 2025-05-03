from app.db.config import get_db_settings, build_sqlalchemy_url

def test_get_db_settings_keys():
    config = get_db_settings()
    expected_keys = {"HOST", "PORT", "NAME", "USER", "PASSWORD", "POOL_SIZE", "MAX_OVERFLOW", "POOL_TIMEOUT", "POOL_RECYCLE", "ECHO"}
    assert expected_keys.issubset(set(config.keys()))

def test_sqlalchemy_url_format():
    config = {
        "HOST": "localhost",
        "PORT": "5432",
        "NAME": "testdb",
        "USER": "testuser",
        "PASSWORD": "testpass"
    }
    url = build_sqlalchemy_url(config)
    assert url == "postgresql+psycopg2://testuser:testpass@localhost:5432/testdb"
