# auth.py test code
# 2022 * not updated with the newer version of working files

import pytest
from website.models import User
#from website import db, create_test_app
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

def test_success_login_coach(client):

    response = client.get('/login')
    assert response.status_code == 200  #assert login page is stable
    assert b'email' in response.data    # assert email and password boxes are available to users for login
    assert b'password' in response.data

    with client:
        response = client.post('/login', data={"email": "hannah@colby.edu",
            "password": "1234567890"}) # try to login with coach data
        assert response.status_code == 302  #assert redirect to dashboard
        assert b'Redirecting' in response.data

        response = client.get('/teamView/<team_name>', follow_redirects=True)
        assert response.status_code == 200 #dashboard is stable
        assert b"Home" in response.data
    
def test_success_login_admin(client):
    response = client.get('/login')
    assert response.status_code == 200  #assert login page is stable
    
    # assert email and password boxes are available to users for login
    assert b'email' in response.data
    assert b'password' in response.data

    with client:
        # try to login with admin data
        response = client.post("/login", data={"email": "anne@colby.edu",
            "password": "1234567890"})
        #assert redirect to dashboard, login is working
        assert response.status_code == 302
        assert b'Redirecting' in response.data

        # follow direct to dashboard
        response = client.get('/adminView', follow_redirects=True)
       
        # assert dashboard is stable
        assert response.status_code == 200
        assert b"Home" in response.data

def test_success_login_athlete(client):
    response = client.get('/login')
    #assert login page is stable
    assert response.status_code == 200
    # assert email and password boxes are available to users for login
    assert b'email' in response.data
    assert b'password' in response.data

    with client:
        # try to login with athlete data
        response = client.post("/login", data={"email": "matt@colby.edu",
            "password": "1234567890"})
        #assert redirect to dashboard, login is working
        assert response.status_code == 302
        assert b'Redirecting' in response.data

        # follow direct to dashboard
        response = client.get('/athleteView/<first_name><last_name>', follow_redirects=True)
        # assert dashboard is stable
        assert response.status_code == 200
        assert b"Home" in response.data
        
def test_failed_login_wrong_email(client):
    response = client.get('/login')
    #assert login page is stable
    assert response.status_code == 200
    # assert email and password boxes are available to users for login
    assert b'email' in response.data
    assert b'password' in response.data

    with client:
        # try to login with with wrong email 
        response = client.post("/login", data={"email": "mattew24@colby.edu",
            "password": "1234567890"})
        #assert page is still stable
        assert response.status_code == 200
        #assert correct error message is displayed
        assert b'Email does not exist' in response.data


def test_failed_login_wrong_password(client):
    response = client.get('/login')
    #assert login page is stable
    assert response.status_code == 200
    # assert email and password boxes are available to users for login
    assert b'email' in response.data
    assert b'password' in response.data

    with client:
        # try to login with with wrong password 
        response = client.post("/login", data={"email": "matt@colby.edu",
            "password": "GruIsCool!"})
        #assert page is still stable
        assert response.status_code == 200
        #assert correct error message is displayed
        assert b'Incorrect password' in response.data



def test_failed_login_undefined_role(client):
    response = client.get('/login')
    #assert login page is stable
    assert response.status_code == 200
    # assert email and password boxes are available to users for login
    assert b'email' in response.data
    assert b'password' in response.data

    with client:
        # try to login with with unidentified role
        response = client.post("/login", data={"email": "gru@colby.edu",
            "password": "GruIsCool!"})
        #assert page is still stable
        assert response.status_code == 200
        #assert correct error message is displayed
        assert b'User role not recognized, please contact admin' in response.data

    
def test_logout(client):
    # first login, this is as coach
    with client:
        response = client.post("/login", data={
            "email": "hannah@colby.edu",
            "password": "1234567890"
        })

        #try to logout, follows redirect
        response = client.get('/logout', follow_redirects=True)
        #assert immediate redirect
        #assert response.status_code == 302
        #assert b'Redirecting' in response.data

        #response = client.get('/login', follow_redirects=True)
    
        #redirects to login page, that page is stable
        assert response.status_code == 200
        assert b'Login' in response.data

