# logic for the data from csv files converted for charts
# charts details
# 2022 revised 2026

# imports
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, login_user
from . import db
from .models import User, Hawkins, parse_csv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import pandas as pd
import json
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# create blueprint
views = Blueprint('views', __name__)

# goes to login
@views.route("/", methods=['GET', 'POST'])
def home():
    return redirect(url_for('auth.login'))

# executes the save to drive but does not change html page
@views.route("/files", methods=['GET', 'POST'])
@login_required
def files():
    return render_template("adminView.html", user=current_user)

# quarantines a safe number value and avoids NaN
def safe_avg(value):
    # Case 1: pandas Series
    if isinstance(value, pd.Series):
        if value.empty:
            return 0
        return round(value.mean(), 2)

    # Case 2: numeric value (float, int, numpy number)
    if isinstance(value, (int, float, np.number)):
        if pd.isna(value):
            return 0
        return round(value, 2)

    # Fallback
    return 0

# admin view
@views.route("/adminView", methods=['GET', 'POST'])
@login_required
def adminView():

    # load CSVs
    dfR = pd.read_csv('website/data/readiness.csv')
    dfS = pd.read_csv('website/data/sleep.csv')
    dfN = pd.read_csv('website/data/nutrition.csv')

    # available teams 
    TeamNames = sorted(dfR["Team"].dropna().unique().tolist())

    # overall averages for all teams
    readinessAvg = safe_avg(dfR["Score"].mean())
    hoursAvg = safe_avg(dfS["Hours"].mean())
    qualityAvg = safe_avg(dfS["Quality"].mean())
    calAvg = safe_avg(dfN["Calorie Intake"].mean())

    # team-level values derived from CSVs
    team_sleep = dfS.groupby("Team")["Hours"].mean()
    team_readiness = dfR.groupby("Team")["Score"].mean()

    teamValues1 = team_sleep.tolist()
    teamValues2 = team_readiness.tolist()

    # graph data
    readinessL = ["Score"]
    readinessV = [readinessAvg]

    sleepL = ["Hours", "Quality"]
    h = [hoursAvg]
    q = [qualityAvg]

    nutritionL = ["Calorie Intake"]
    nutritionV = [calAvg]

    # get all of the stats
    team_stats = (
        dfR.groupby("Team")["Score"].mean()
        .to_frame("readiness")
        .join(dfS.groupby("Team")[["Hours", "Quality"]].mean())
        .join(dfN.groupby("Team")["Calorie Intake"].mean())
        .round(1)
        .reset_index()
    )

    # create dictionary
    team_stats = team_stats.to_dict(orient="records")

    # pie charts
    fig = make_subplots(
        rows=1,
        cols=4,
        subplot_titles=[
            "Readiness",
            "Sleep Quality",
            "Sleep Hours",
            "Nutrition",
        ],
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
        ],
        horizontal_spacing=0.12,
        vertical_spacing=0.4,
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=readinessAvg,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "yellow"}
            },
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=qualityAvg,
            gauge={
                "axis": {"range": [0, 10]},
                "bar": {"color": "purple"}
            },
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=hoursAvg,
            gauge={
                "axis": {"range": [0, 12]},
                "bar": {"color": "blue"}
            },
        ),
        row=1, col=3
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=calAvg,
            gauge={
                "axis": {"range": [0, 4000]},
                "bar": {"color": "orange"}
            },
        ),
        row=1, col=4
    )

    for ann in fig.layout.annotations:
        ann.y += 0.2

    fig.update_layout(
        showlegend=False,
        width=1100,
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )

    graphJSON = json.loads(fig.to_json())

    return render_template(
        "adminView.html",
        graphJSON=graphJSON,
        team_stats=team_stats
    )

# team view
@views.route("/teamView/<team_name>", methods=['GET', 'POST'])
@login_required
def teamView(team_name):

    #read in data
    dfR = pd.read_csv('website/data/readiness.csv')
    dfS = pd.read_csv('website/data/sleep.csv')
    dfN = pd.read_csv('website/data/nutrition.csv')

    # normalize names (capitals)
    team_name = team_name.strip().lower()

    # ensures team names are all strings
    dfR["Team"] = dfR["Team"].astype(str).str.strip().str.lower()
    dfS["Team"] = dfS["Team"].astype(str).str.strip().str.lower()
    dfN["Team"] = dfN["Team"].astype(str).str.strip().str.lower()

    # clean data by converting to numerics nd avoiding NaN
    dfR["Score"] = pd.to_numeric(dfR["Score"], errors="coerce")
    dfS["Hours"] = pd.to_numeric(dfS["Hours"], errors="coerce")
    dfS["Quality"] = pd.to_numeric(dfS["Quality"], errors="coerce")
    dfN["Calorie Intake"] = pd.to_numeric(dfN["Calorie Intake"], errors="coerce")

    # makes athlete names strings
    dfR["Name"] = dfR["Name"].astype(str)
    dfS["Name"] = dfS["Name"].astype(str)
    dfN["Name"] = dfN["Name"].astype(str)

    # then filter to readiness, sleep, nutrition
    team_r = dfR[dfR["Team"] == team_name]
    team_s = dfS[dfS["Team"] == team_name]
    team_n = dfN[dfN["Team"] == team_name]

    # ensure safe and valid number
    readinessAvg = safe_avg(team_r["Score"])
    hoursAvg = safe_avg(team_s["Hours"])
    qualityAvg = safe_avg(team_s["Quality"])
    calAvg = safe_avg(team_n["Calorie Intake"])

    # athlete breakdown
    # readiness per athlete
    readiness_avg = (
        dfR[dfR["Team"] == team_name]
            .groupby("Name", as_index=False)["Score"]
            .mean()
            .rename(columns={"Score": "Readiness"})
    )

    # sleep per athlete
    sleep_avg = (
        dfS[dfS["Team"] == team_name]
            .groupby("Name", as_index=False)[["Hours", "Quality"]]
            .mean()
    )

    # nutrition per athlete
    nutrition_avg = (
        dfN[dfN["Team"] == team_name]
            .groupby("Name", as_index=False)["Calorie Intake"]
            .mean()
            .rename(columns={"Calorie Intake": "Calories"})
    )

    # merge everything
    athlete_stats = (
        readiness_avg
            .merge(sleep_avg, on="Name", how="left")
            .merge(nutrition_avg, on="Name", how="left")
            .round(1)
    )

    # convert to dictionary
    athlete_stats = athlete_stats.to_dict(orient="records")

    # make pie charts
    fig = make_subplots(
    rows=1,
    cols=4,
    subplot_titles=["Readiness", "Sleep Quality", "Sleep Hours", "Nutrition"],
    specs=[
        [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
    ],
    horizontal_spacing=0.12,
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=readinessAvg,
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "yellow"}
            },
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=qualityAvg,
            gauge={
                "axis": {"range": [0, 10]},
                "bar": {"color": "purple"}
            },
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=hoursAvg,
            gauge={
                "axis": {"range": [0, 12]},  
                "bar": {"color": "blue"}
            },
        ),
        row=1, col=3
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=calAvg,
            gauge={
                "axis": {"range": [0, 4000]}, 
                "bar": {"color": "orange"}
            },
        ),
        row=1, col=4
    )

    fig.update_layout(
        showlegend=False,
        width=1100,
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )

    graphJSON = json.loads(fig.to_json());

    return render_template(
        "teamView.html",
        user=current_user,
        graphJSON=graphJSON,
        athlete_stats=athlete_stats,
        TeamName=team_name
    )


# athlete view
@views.route("/athleteView/<athlete_name>", methods=["GET", "POST"])
@login_required
def athleteView(athlete_name):

    # load data
    dfR = pd.read_csv("website/data/readiness.csv")
    dfS = pd.read_csv("website/data/sleep.csv")
    dfN = pd.read_csv("website/data/nutrition.csv")

    # normalize names
    athlete_name = athlete_name.strip()

    for df in (dfR, dfS, dfN):
        df["Name"] = df["Name"].astype(str).str.strip()

    # force data to numerics and avoid NaN
    dfR["Score"] = pd.to_numeric(dfR["Score"], errors="coerce")
    dfS["Hours"] = pd.to_numeric(dfS["Hours"], errors="coerce")
    dfS["Quality"] = pd.to_numeric(dfS["Quality"], errors="coerce")
    dfN["Calorie Intake"] = pd.to_numeric(dfN["Calorie Intake"], errors="coerce")

    # filter into readiness, sleep, and nutrition
    aR = dfR[dfR["Name"] == athlete_name]
    aS = dfS[dfS["Name"] == athlete_name]
    aN = dfN[dfN["Name"] == athlete_name]

    readinessAvg = safe_avg(aR["Score"])
    qualityAvg   = safe_avg(aS["Quality"])
    hoursAvg     = safe_avg(aS["Hours"])
    calAvg       = safe_avg(aN["Calorie Intake"])

    # make pie charts
    fig = make_subplots(
        rows=1,
        cols=4,
        subplot_titles=["Readiness", "Sleep Quality", "Sleep Hours", "Nutrition"],
        specs=[[{"type": "indicator"}] * 4],
        horizontal_spacing=0.12
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=readinessAvg,
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "yellow"}},
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=qualityAvg,
            gauge={"axis": {"range": [0, 10]}, "bar": {"color": "purple"}},
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=hoursAvg,
            gauge={"axis": {"range": [0, 12]}, "bar": {"color": "blue"}},
        ),
        row=1, col=3
    )

    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=calAvg,
            gauge={"axis": {"range": [0, 4000]}, "bar": {"color": "orange"}},
        ),
        row=1, col=4
    )

    fig.update_layout(
        width=1100,
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    graphJSON = json.loads(fig.to_json())

    return render_template(
        "athleteView.html",
        user=current_user,
        athlete_name=athlete_name,
        graphJSON=graphJSON
    )
