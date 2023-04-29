from pybaseball import standings
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import date

today = date.today()
data=standings(2023)

wins=pd.DataFrame()

for division in data:
    division_df=pd.DataFrame(division, columns=['Tm','W','L','W-L%','GB'])
    wins = pd.concat([wins, division_df], axis=0)

data = [
    {"Name": "Chris", "Team": "Houston Astros"},
    {"Name": "Daniel", "Team": "Atlanta Braves"},
    {"Name": "Kevin", "Team": "New York Yankees"},
    {"Name": "Drew", "Team": "Los Angeles Dodgers"},
    {"Name": "Casey", "Team": "San Diego Padres"},
    {"Name": "Andrew", "Team": "New York Mets"},
    {"Name": "Brandon", "Team": "Toronto Blue Jays"},
    {"Name": "Brandon", "Team": "St. Louis Cardinals"},
    {"Name": "Andrew", "Team": "Seattle Mariners"},
    {"Name": "Casey", "Team": "Philadelphia Phillies"},
    {"Name": "Drew", "Team": "Milwaukee Brewers"},
    {"Name": "Kevin", "Team": "Cleveland Guardians"},
    {"Name": "Daniel", "Team": "Minnesota Twins"},
    {"Name": "Chris", "Team": "Tampa Bay Rays"},
    {"Name": "Chris", "Team": "Chicago White Sox"},
    {"Name": "Daniel", "Team": "Los Angeles Angels"},
    {"Name": "Kevin", "Team": "Baltimore Orioles"},
    {"Name": "Drew", "Team": "Texas Rangers"},
    {"Name": "Casey", "Team": "Boston Red Sox"},
    {"Name": "Andrew", "Team": "Arizona Diamondbacks"},
    {"Name": "Brandon", "Team": "San Francisco Giants"},
    {"Name": "Brandon", "Team": "Cincinnati Reds"},
    {"Name": "Andrew", "Team": "Miami Marlins"},
    {"Name": "Casey", "Team": "Chicago Cubs"},
    {"Name": "Drew", "Team": "Detroit Tigers"},
    {"Name": "Kevin", "Team": "Kansas City Royals"},
    {"Name": "Daniel", "Team": "Pittsburgh Pirates"},
    {"Name": "Chris", "Team": "Colorado Rockies"},
]

owners = pd.DataFrame(data)

combined=owners.merge(wins, left_on='Team', right_on='Tm')

combined=combined[['Name','Team','W','L']]
combined['W']=combined['W'].astype(int)
combined=combined.sort_values('W', ascending=False)
summary=combined.groupby('Name')['W'].sum()

summary_sorted=summary.sort_values(ascending=False)

summary_df=pd.DataFrame(summary_sorted).reset_index()

slack_token="xoxb-138249782035-5117499680852-eL0fNMCzaksJxVMrErLr9yWN"
#slack_token="xoxb-1130816828471-5104528585302-RTwcZx6CWzoNIbqwKERbrGnf"
client = WebClient(token=slack_token)

summary_df = summary_df.set_index('Name')
summary_df= summary_df.rename(columns={"W":"Win Total"})
# Send csv file
client.files_upload(
channels = "mlb",
#channels = "bot-testing",
initial_comment = "{} Wins League Standings:".format(today),
filename = "wins.csv",
content = summary_df) 

combined=combined.set_index('Name')
client.files_upload(
channels = "mlb",
#channels = "bot-testing",
initial_comment = "{} MLB Win/Loss Summary:".format(today),
filename = "team_records.csv",
content = combined)

