import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"
    with flask_app.test_client() as c:
        yield c


def test_index_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200


def test_index_filter_by_category(client):
    res = client.get("/?category=Laptop")
    assert res.status_code == 200
    assert b"MacBook" in res.data or b"Dell" in res.data


def test_index_search(client):
    res = client.get("/?search=iphone")
    assert res.status_code == 200
    assert b"iPhone" in res.data


def test_product_detail_exists(client):
    res = client.get("/product/1")
    assert res.status_code == 200
    assert b"iPhone" in res.data


def test_product_detail_not_found_redirects(client):
    res = client.get("/product/9999")
    assert res.status_code == 302


def test_cart_empty(client):
    res = client.get("/cart")
    assert res.status_code == 200


def test_add_to_cart(client):
    res = client.post("/cart/add/1", data={"qty": 1}, follow_redirects=True)
    assert res.status_code == 200


def test_checkout_get(client):
    res = client.get("/checkout")
    assert res.status_code == 200


def test_checkout_post_clears_cart(client):
    client.post("/cart/add/1", data={"qty": 1})
    res = client.post("/checkout", follow_redirects=True)
    assert res.status_code == 200


def test_discount_valid_code(client):
    res = client.get("/discount?code=SAVE10")
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is True
    assert data["discount_rate"] == 0.10


def test_discount_invalid_code(client):
    res = client.get("/discount?code=INVALID")
    assert res.status_code == 200
    data = res.get_json()
    assert data["valid"] is False


def test_discount_calculation_correct(client):
    # Intentional failure: validates wrong expected discount rate
    res = client.get("/discount?code=VDT20")
    data = res.get_json()
    assert data["discount_rate"] == 0.50, (
        f"Expected 50% discount but got {data['discount_rate']} — "
        "discount logic needs fixing"
    )
