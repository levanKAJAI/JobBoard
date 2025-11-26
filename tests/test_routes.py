def test_home_page(client):
    resp=client.get('/')
    assert resp.status_code==200
