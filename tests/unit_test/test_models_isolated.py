# checks whether SQLAlchemy models can be instantiated correctly and whether their attributes are stored as expected
# 2022

import pytest
from website.models import User, Team, Note, Hawkins, Nutrition, Sleep, Readiness

def test_create_user():
    #create user object
    user = User(id = 1, email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")

    #verify user information
    print("Email: " + user.email +" == hannah25@colby.edu")
    print("First name: "+ user.first_name + " == hannah")
    print("Last name: " + user.last_name + " == soria")
    print("Password: "+ user.password +" == 1234567")
    print("Role: " + user.role + " == athlete")

    #test if user object can be created, test data is stored correctly
    assert user != None
    assert user.email == "hannah25@colby.edu"
    assert user.first_name == "hannah"
    assert user.last_name =="soria"
    assert user.password == "1234567"
    assert user.role == "athlete"


def test_create_team():
    #create user to add to team
    hannah = User(email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")

    #create team object
    team = Team(name = "Men's Swim", users = [hannah])

    #verify team information
    print("Team name: " + team.name +" == Men's Swim")
    print("Player in team is: ")
    for player in team.users:
        print(player)
    print("Player in team should be: hannah")

    #verify backref between user and team
    print("user hannah is on team: " + hannah.teams[0].name )

    #test if team object can be created, test data is stored correctly
    assert hannah != None
    assert team != None
    assert team.name == "Men's Swim"
    assert team.users[0].first_name == "hannah"
    assert hannah.teams[0].name == "Men's Swim"

def test_create_Note():
    #create user
    hannah = User(id = 1,email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")
   
    #create Note object for user
    note = Note(content= "testing", user_id = hannah.id)

    #verify Note content
    print("Note content: " + note.content + "testing")
    print("Note user_id is: " + str(note.user_id))
    print("Note user id should be: " + str(hannah.id))
    
    #test if note object can be created, test data is stored correctly
    assert hannah != None
    assert note != None
    assert hannah.id != None
    assert note.content == "testing"
    assert note.user_id == hannah.id

def test_create_Hawkins():
    #create user
    hannah = User(id = 1,email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")
   
    #create Hawkins object for user
    hdata = Hawkins(date= "11/29/2022", peak_force = 20,
        user_id = hannah.id)

    #verify Hawkins object content
    print("Hawkins date: " + str(hdata.date) + "== 11/29/2022")
    print("Peak force: " + str(hdata.peak_force) + " == 20")
    print("Hawkins user_id is: " + str(hdata.user_id))
    print("Hawkins user id should be: " + str(hannah.id))
    
    #test if hawkins object can be created, test data is stored correctly
    assert hannah != None
    assert hdata != None
    assert hannah.id != None
    assert hdata.date == "11/29/2022"
    assert hdata.peak_force == 20
    assert hdata.user_id == hannah.id


def test_create_Sleep():
    #create user
    hannah = User(id = 1,email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")
   
    #create sleep object for user
    sdata = Sleep(date= "11/29/2022", TotalSleepScore = 80,
        TotalSleepDuration = 7, user_id = hannah.id)

    #verify Sleep object content
    print("Sleep data date: " + str(sdata.date) + "== 11/29/2022")
    print("Total sleep score: " + str(sdata.TotalSleepScore) + " == 80")
    print("Total sleep duration:" + str(sdata.TotalSleepDuration) + " == 7")
    print("Sleep user_id is: " + str(sdata.user_id))
    print("Sleep user id should be: " + str(hannah.id))
    
    #test if sleep object can be created, test data is stored correctly
    assert hannah != None
    assert sdata != None
    assert hannah.id != None
    assert sdata.date == "11/29/2022"
    assert sdata.TotalSleepScore == 80
    assert sdata.TotalSleepDuration == 7
    assert sdata.user_id == hannah.id

def test_create_Nutrition():
    #create user
    hannah = User(id = 1,email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")
   
    #create Nutrition object for user
    ndata = Nutrition(date= "11/29/2022", calories = 2500, user_id = hannah.id)

    #verify Nutrition object content
    print("Nutrition data date: " + str(ndata.date) + "== 11/29/2022")
    print("Total calories: " + str(ndata.calories) + " == 2500")
    print("Nutrition user_id is: " + str(ndata.user_id))
    print("Nutrition user id should be: " + str(hannah.id))
    
    #test if Nutrition object can be created, test data is stored correctly
    assert hannah != None
    assert ndata != None
    assert hannah.id != None
    assert ndata.date == "11/29/2022"
    assert ndata.calories == 2500
    assert ndata.user_id == hannah.id

def test_create_Readiness():
     #create user
    hannah = User(id = 1,email = "hannah25@colby.edu", first_name = "hannah",
    last_name = "soria", password = "1234567", role = "athlete")
   
    #create readiness object for user
    rdata = Readiness(date= "11/29/2022", RecoveryIndexScore = 80,
        ReadinessScore = 75, user_id = hannah.id)

    #verify readiness object content
    print("Readiness data date: " + str(rdata.date) + "== 11/29/2022")
    print("Recovery Index Score: " + str(rdata.RecoveryIndexScore) + " == 80")
    print("Readiness Score:" + str(rdata.ReadinessScore) + " == 75")
    print("Readiness user_id is: " + str(rdata.user_id))
    print("Readiness user id should be: " + str(hannah.id))
    
    #test if readiness object can be created, test data is stored correctly
    assert hannah != None
    assert rdata != None
    assert hannah.id != None
    assert rdata.date == "11/29/2022"
    assert rdata.RecoveryIndexScore == 80
    assert rdata.ReadinessScore == 75
    assert rdata.user_id == hannah.id