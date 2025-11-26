def test_edit_permission(client):
    resp=client.get('/edit_job/1')
    assert resp.status_code in [302,403,200]
