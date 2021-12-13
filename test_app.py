import pytest

from main import app


@pytest.fixture
def client():
    with app.test_client() as client:
        # with app.app_context():
        yield client


def test_1vs1_will_throw(client):
    payload = {
        "_links": {"self": {"href": "http://me"}},
        "arena": {
            'dims': [20, 20],
            "state": {
                "http://me": {"x": 3, "y": 3, "direction": "E"},
                "http://him": {
                    "x": 11,
                    "y": 3,
                    "direction": "E",
                },
            },
        },
    }

    response = client.post("/", json=payload)
    assert response.status_code == 200
    assert response.json == "T"
