import threading

import pytest

import mock_model


@pytest.fixture(scope="session", autouse=True)
def offline_model():
    """Scripted OpenAI-compatible server; the SDK reaches it through BYOK (provider=)."""
    srv = mock_model.serve()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    import os
    os.environ["LAB_PROVIDER_URL"] = "http://127.0.0.1:8765/v1"
    os.environ["LAB_MODEL"] = "mock-model"
    yield
    srv.shutdown()
