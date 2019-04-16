"""Unit tests for cron API."""


def test_cron_bad_originator(app):
    """Test cron API from bad origin address."""
    token = app.cron_helper.get_cron_token()
    client = app.test_client()
    response = client.post(
        '/api/cron/1234/unit_test',
        environ_base={'REMOTE_ADDR': '192.168.1.1'}
    )

    assert response.status_code == 403

    # Make sure a new token was not generated
    assert token == app.cron_helper.get_cron_token()


def test_cron_bad_token(app):
    """Test cron API from bad cron token."""
    token = app.cron_helper.get_cron_token()
    client = app.test_client()
    response = client.post(
        '/api/cron/1234/unit_test',
        environ_base={'REMOTE_ADDR': '127.0.0.1'}
    )

    assert response.status_code == 401

    # Make sure a new token was not generated
    assert token == app.cron_helper.get_cron_token()


def test_cron_good_token(app):
    """Test cron API with correct cron token."""
    token = app.cron_helper.get_cron_token()
    client = app.test_client()
    response = client.post(
        '/api/cron/{}/unit_test'.format(token),
        environ_base={'REMOTE_ADDR': '127.0.0.1'}
    )

    assert response.status_code == 200

    # Make sure a new token was generated
    assert token != app.cron_helper.get_cron_token()


def test_cron_bad_task(app):
    """Test cron API with correct cron token but invalid task."""
    token = app.cron_helper.get_cron_token()
    client = app.test_client()
    response = client.post(
        '/api/cron/{}/bad_task'.format(token),
        environ_base={'REMOTE_ADDR': '127.0.0.1'}
    )

    assert response.status_code == 403

    # Make sure a new token was not generated
    assert token == app.cron_helper.get_cron_token()