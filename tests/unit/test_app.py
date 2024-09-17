# Unit Testing
import pytest
from microblog import app

# Testing website HTTP Get requests
@pytest.fixture
def test_website():
    app.config.update({
        "TESTING": True,
    })
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

