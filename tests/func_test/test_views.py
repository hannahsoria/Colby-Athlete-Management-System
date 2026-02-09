# views.py test code 
# 2022 * not updated with the newer version of working files

from website import create_test_app
import json
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pytest
    
def create_test_graph():
    # name = athlete_name[0] + athlete_name[1] 
    dfR = pd.read_csv('website/data/readiness.csv')
    readinessAvg = dfR["Score"].mean().astype(int)

    dfS = pd.read_csv('website/data/sleep.csv')
    hoursAvg = dfS["Hours"].mean().astype(int)

    qualityAvg = dfS["Quality"].mean().astype(int)

    dfN = pd.read_csv('website/data/nutrition.csv')
    calAvg = dfN["Calorie Intake"].mean().astype(int)

    dfT = pd.read_csv('website/data/team.csv')
    teamValues1 = dfT["Hours"].tolist()
    teamValues2 = dfT["Readiness"].tolist()

    readinessL = ["Score"]
    readinessV = [readinessAvg]

    sleepL = ["Hours", "Quality"]
    h = [hoursAvg]
    q = [qualityAvg]

    nutritionL = ["Calorie Intake"]
    nutritionV = [calAvg]

    fig = make_subplots(rows=1, cols=4, column_widths=[.2, .2, .2, .5],
                        subplot_titles=["Readiness", "Sleep", "Nutrition",
                                        "Team Readiness"],
                        horizontal_spacing=0.1,
                        specs=[[{"type": "pie"}, {"type": "pie"},
                                {"type": "pie"}, {"type": "scatter"}]])

    # READINESS GRAPH
    fig.add_trace(go.Pie(values=readinessV, labels=readinessL, hole=.5,
                         title="Readiness", textfont=dict(color="white")),
                  row=1, col=1)

    # SLEEP GRAPH
    fig.add_trace(go.Pie(title="Sleep", hole=0.5, sort=False,
                         direction='clockwise', values=q,
                         textposition='inside',
                         marker={'line': {'color': 'white', 'width': 1}}),
                  row=1, col=2)

    fig.add_trace(go.Pie(hole=0.7, sort=False, direction='clockwise', values=h,
                         labels=sleepL, textposition='inside',
                         marker={'colors': ['green', 'red', 'blue'],
                                 'line': {'color': 'white', 'width': 1}}),
                  row=1, col=2)

    # NUTRITION GRAPH
    fig.add_trace(go.Pie(values=nutritionV, labels=nutritionL, hole=.5,
                         title="Nutrition", textfont=dict(color="white")),
                  row=1, col=3)

    # TEAM GRAPH
    fig.add_trace(go.Scatter(x=teamValues1, y=teamValues2), row=1, col=4)

    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)',
                      'paper_bgcolor': 'rgba(0,0,0,0)', })

    fig.update_layout(margin=dict(l=50, r=0, t=0, b=0))
    fig.update_layout(showlegend=False)
    fig.update_layout(width=1100, height=300)
    fig.update_layout(font_color="white")
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def test_home_admin(client):
    response=client.get('/')
    
    assert response.status_code == 302 #goes to login page
    assert b'Redirecting' in response.data
    assert b'login' in response.data
 
    with client:
        response = client.post("/login", 
            data={"email": "anne@colby.edu",
                "password": "1234567890"})
    
        #print(response.data)
        #redirects to adminView page, aka admin dashboard/home
        assert response.status_code == 302 
        assert b'Redirecting' in response.data
        assert b'adminView' in response.data 

def test_home_coach(client):
    response=client.get('/')
    
    assert response.status_code == 302 #goes to login page
    assert b'Redirecting' in response.data
    assert b'login' in response.data
 
    with client:
        response = client.post("/login", 
            data={"email": "hannah@colby.edu",
                "password": "1234567890"})
    
        #print(response.data)
        #redirects to teamView page, aka coach dashboard/home
        assert response.status_code == 302 
        assert b'Redirecting' in response.data
        assert b'teamView' in response.data 

def test_home_athlete(client):
    response=client.get('/')
    
    #redirect to login page
    assert response.status_code == 302 
    assert b'Redirecting' in response.data
    assert b'login' in response.data
 
    with client:
        response =client.post("/login", 
            data={"email": "matt@colby.edu",
                "password": "1234567890"})
    
        #print(response.data)
        #redirects to coachView page, aka coach dashboard/home
        assert response.status_code == 302 
        assert b'Redirecting' in response.data
        assert b'athleteView' in response.data


#admin has no if statments within the python code
#graphs are hard coded in html, so as long as it returns
#the correct page we are okay
def test_adminView(client):
    with client:
        client.post("/login", 
                data={"email": "anne@colby.edu",
                "password": "1234567890"})

        response = client.get('/adminView')
        #print(response.data)
        assert response.status == '200 OK'
        assert b'Home' in response.data

        


def test_athleteView(client):
    with client:
        #login user
        client.post("/login", 
                data={"email": "matt@colby.edu",
                "password": "1234567890"})

        response = client.get('athleteView/<first_name><last_name>')
        print(response.data)
        #page is stable, with correct user into
        assert response.status == '200 OK'
        assert b'Home' in response.data
        assert b'Matt' in response.data

        #creates graph with expected data
        graph = create_test_graph()

        #asserts graphs are created and have expected data
        assert b'Readiness' in response.data
        assert b'Sleep' in response.data
        assert b'Nutrition' in response.data
        assert bytes(graph, 'utf-8') in response.data
        

def test_teamView(client):
    with client:
        #login user
        client.post("/login", 
                data={"email": "hannah@colby.edu",
                "password": "1234567890"})

        response = client.get('teamView/<team_name>')
        print(response.data)
        #page is stable, with correct user into
        assert response.status == '200 OK'
        assert b'Home' in response.data
        assert b'Hannah' in response.data
        assert b'team_name' in response.data

        #creates graph with expected data
        graph = create_test_graph()

        #asserts graphs are created and have expected data
        assert b'Readiness' in response.data
        assert b'Sleep' in response.data
        assert b'Nutrition' in response.data
        assert bytes(graph, 'utf-8') in response.data

        

        
        
    
    
