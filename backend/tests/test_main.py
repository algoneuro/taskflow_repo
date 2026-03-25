def test_cors_headers(client):
    """OPTIONS запрос должен возвращать CORS заголовки"""
    response = client.options("/", headers={
        "Origin": "http://localhost:5500",
        "Access-Control-Request-Method": "GET"
    })
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers