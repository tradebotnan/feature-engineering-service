from app.utils.env_loader import load_env

def test_load_env():
    config = load_env()
    assert 'INPUT_PATH' in config
    assert 'OUTPUT_PATH' in config
    assert 'LOG_LEVEL' in config
