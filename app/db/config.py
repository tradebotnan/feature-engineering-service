from app.utils.env_loader import get_env_variable

def get_db_settings() -> dict:
    return {
        "HOST": get_env_variable("HOST", "localhost"),
        "PORT": get_env_variable("PORT", "5432"),
        "NAME": get_env_variable("NAME", "tradebotnan"),
        "USER": get_env_variable("USER", "postgres"),
        "PASSWORD": get_env_variable("PASSWORD", "postgres"),
        "POOL_SIZE": int(get_env_variable("POOL_SIZE", "10")),
        "MAX_OVERFLOW": int(get_env_variable("MAX_OVERFLOW", "20")),
        "POOL_TIMEOUT": int(get_env_variable("POOL_TIMEOUT", "30")),
        "POOL_RECYCLE": int(get_env_variable("POOL_RECYCLE", "1800")),
        "ECHO": get_env_variable("SQLALCHEMY_ECHO", "false").lower() == "true",
    }

def build_sqlalchemy_url(settings: dict) -> str:
    return (
        f"postgresql+psycopg2://{settings['USER']}:{settings['PASSWORD']}@"
        f"{settings['HOST']}:{settings['PORT']}/{settings['NAME']}"
    )