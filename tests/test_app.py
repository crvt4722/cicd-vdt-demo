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


def test_api_products_returns_all(client):
    res = client.get("/api/products")
    assert res.status_code == 200
    data = res.get_json()
    assert "products" in data
    assert data["count"] == 8


def test_api_products_filter_by_category(client):
    res = client.get("/api/products?category=Laptop")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 2
    names = [p["name"] for p in data["products"]]
    assert "MacBook Air M3" in names
    assert "Dell XPS 15" in names


def test_api_products_search(client):
    res = client.get("/api/products?search=airpods")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 1
    assert data["products"][0]["name"] == "AirPods Pro 2"


def test_api_products_no_results(client):
    res = client.get("/api/products?category=NonExistent")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 0
    assert data["products"] == []
