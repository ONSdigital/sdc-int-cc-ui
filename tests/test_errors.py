import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            pass
        yield client


class TestErrors:
    def disable_test_404_renders_template(self, client):
        response = client.get('/unknown-path')
        assert response.status_code == 404
        print(response)
        contents = str(response.data)
        assert 'Page not found' in contents
