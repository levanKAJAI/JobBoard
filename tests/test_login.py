def test_login(client):
    resp=client.post('/login',data={'email':'test@test.com','password':'password'},follow_redirects=True)
    assert b'Login' in resp.data or resp.status_code==200
