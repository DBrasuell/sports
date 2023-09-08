import nfl_data_py as nfl
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG)
import numpy as np
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import date
from config import slack_token

def get_nfl_wins():
    df=nfl.import_schedules([2022])

    conditions = [
        df['result'] > 0,
        df['result'] < 0,
        df['result'].isna()
    ]

    choices1 = [
        df['home_team'],
        df['away_team'],
        np.nan
    ]

    choices2 = [
        df['away_team'],
        df['home_team'],
        np.nan
    ]

    df['win'] = np.select(conditions, choices1, default=np.nan)
    df['lose'] = np.select(conditions, choices2, default=np.nan)


    df=df[['week','win','lose']]

    win_df = df[['week', 'win']].copy()
    win_df['result'] = 'W'
    win_df.rename(columns={'win': 'team'}, inplace=True)

    lose_df = df[['week', 'lose']].copy()
    lose_df['result'] = 'L'
    lose_df.rename(columns={'lose': 'team'}, inplace=True)

    # Concatenate the two DataFrames
    combined_df = pd.concat([win_df, lose_df]).reset_index()
    df_cleaned = combined_df.dropna()
    df_cleaned.drop_duplicates(subset=['week','team'], inplace=True)

    # Pivot the DataFrame to get the desired format
    pivot_df = df_cleaned.pivot(index='team', columns='week', values='result')

    pivot_df.fillna('X', inplace=True)

    win_counts=pd.DataFrame(win_df['team'].value_counts()).reset_index()
    win_counts.rename(columns={'index': 'team', 'team':'wins'}, inplace=True)

    # Sample data
    data = {
        'owner': ['Justin', 'Drew', 'Kevin', 'Andrew', 'Big T', 'Chris', 'Drew', 'Andrew', 'Kevin', 'Josh', 'Drew', 'Josh', 'Kevin', 'Chris', 'Big T', 'Big T', 'Dan', 'Josh', 'Dan', 'Chris', 'Dan', 'Josh', 'Big T', 'Drew', 'Kevin', 'Andrew', 'Justin', 'Justin', 'Justin', 'Andrew', 'Dan', 'Chris'],
        'team': ['Cowboys', 'Jets', 'Bills', 'Lions', 'Falcons', 'Bears', 'Raiders', 'Eagles', 'Broncos', 'Vikings', 'Saints', 'Commanders', 'Packers', 'Bengals', 'Giants', '49ers', 'Chargers', 'Steelers', 'Chiefs', 'Dolphins', 'Rams', 'Ravens', 'Patriots', 'Browns', 'Seahawks', 'Texans', 'Titans', 'Jaguars', 'Panthers', 'Colts', 'Bucs', 'Cardinals']
    }

    owner_df = pd.DataFrame(data)

    # Mapping of NFL team names to their three-letter abbreviations
    team_abbreviations = {
        'Cowboys': 'DAL',
        'Jets': 'NYJ',
        'Bills': 'BUF',
        'Lions': 'DET',
        'Falcons': 'ATL',
        'Bears': 'CHI',
        'Raiders': 'LV',
        'Eagles': 'PHI',
        'Broncos': 'DEN',
        'Vikings': 'MIN',
        'Saints': 'NO',
        'Commanders': 'WAS',
        'Packers': 'GB',
        'Bengals': 'CIN',
        'Giants': 'NYG',
        '49ers': 'SF',
        'Chargers': 'LAC',
        'Steelers': 'PIT',
        'Chiefs': 'KC',
        'Dolphins': 'MIA',
        'Rams': 'LA',
        'Ravens': 'BAL',
        'Patriots': 'NE',
        'Browns': 'CLE',
        'Seahawks': 'SEA',
        'Texans': 'HOU',
        'Titans': 'TEN',
        'Jaguars': 'JAX',
        'Panthers': 'CAR',
        'Colts': 'IND',
        'Bucs': 'TB',
        'Cardinals': 'ARI'
    }

    # Replace team names with abbreviations
    owner_df['team'] = owner_df['team'].map(team_abbreviations)

    merged_df = owner_df.merge(pivot_df, on='team')
    nfl_wins_detail = merged_df.merge(win_counts, on = 'team')
    nfl_wins_detail=nfl_wins_detail.sort_values('owner')
    nfl_wins_summary = pd.DataFrame(nfl_wins_detail.groupby('owner')['wins'].sum())
    nfl_wins_summary = nfl_wins_summary.sort_values('wins',ascending=False)
    
    return nfl_wins_detail, nfl_wins_summary


today = date.today()
nfl_wins_detail, nfl_wins_summary = get_nfl_wins()

channel='nfl'
app = App(token=slack_token)
client = WebClient(token=slack_token)

response = client.chat_postMessage(
            channel=channel,
            text="{} NFL Wins League Standings (Example using 2022 results):".format(today) + f"```{nfl_wins_summary}```"
        ,        mrkdwn=True
    )



#publish to slack    
def push_to_slack(filename, df, slack_token, channel, title, initial_comment):
    
    df.to_csv(filename, index=False)

    client = WebClient(token=slack_token)
    
    response = client.files_upload(
            channels=channel,
            file=filename,
            title=title,
            initial_comment=initial_comment
        )



push_to_slack(filename='NFL Wins League Details.csv', df=nfl_wins_detail, slack_token=slack_token, channel=channel, title='NFL Wins League', initial_comment='')
