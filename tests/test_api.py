def test_insight_today(client):
    r = client.get('/insight/today')
    assert r.status_code == 200
    assert 'risk_level' in r.json()


def test_insight_ussd(client):
    r = client.get('/insight/ussd')
    assert r.status_code == 200
    assert len(r.json()['message']) <= 160


def test_top_gainers(client):
    r = client.get('/stocks/top-gainers')
    assert r.status_code == 200
    data = r.json()
    assert data[0]['ticker'] == 'AAA'
