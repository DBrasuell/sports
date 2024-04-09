from pybaseball import standings
import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG)

from langchain import PromptTemplate, LLMChain
from langchain_anthropic import ChatAnthropic

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from datetime import date

today = date.today()
data=standings(2024)

wins=pd.DataFrame()

for division in data:
    division_df=pd.DataFrame(division, columns=['Tm','W','L','W-L%','GB'])
    wins = pd.concat([wins, division_df], axis=0)


data= [
  {
    "Name": "Kevin",
    "Team": "Los Angeles Dodgers"
  },
  {
    "Name": "Casey", 
    "Team": "Atlanta Braves"
  },
  {
    "Name": "Drew",
    "Team": "Houston Astros"
  },
  {
    "Name": "Daniel",
    "Team": "New York Yankees"
  },
  {
    "Name": "Andrew",
    "Team": "Baltimore Orioles"
  },
  {
    "Name": "Chris",
    "Team": "Philadelphia Phillies"
  },
  {
    "Name": "Kevin",
    "Team": "Toronto Blue Jays"
  },
  {
    "Name": "Casey",
    "Team": "San Francisco Giants"
  },
  {
    "Name": "Drew",
    "Team": "Minnesota Twins"
  },
  {
    "Name": "Daniel",
    "Team": "San Diego Padres"
  },
  {
    "Name": "Andrew",
    "Team": "Seattle Mariners"
  },
  {
    "Name": "Chris",
    "Team": "Texas Rangers"
  },
  {
    "Name": "Kevin",
    "Team": "St. Louis Cardinals"
  },
  {
    "Name": "Casey",
    "Team": "Chicago Cubs"
  },
  {
    "Name": "Drew",
    "Team": "Tampa Bay Rays"
  },
  {
    "Name": "Daniel",
    "Team": "Detroit Tigers"
  },
  {
    "Name": "Andrew",
    "Team": "Arizona Diamondbacks"
  },
  {
    "Name": "Chris",
    "Team": "Cincinnati Reds"
  },
  {
    "Name": "Kevin",
    "Team": "Boston Red Sox"
  },
  {
    "Name": "Casey",
    "Team": "Kansas City Royals"
  },
  {
    "Name": "Drew",
    "Team": "Milwaukee Brewers"
  },
  {
    "Name": "Daniel",
    "Team": "Miami Marlins"
  },
  {
    "Name": "Andrew",
    "Team": "Cleveland Guardians"
  },
  {
    "Name": "Chris",
    "Team": "New York Mets"
  },
  {
    "Name": "Kevin",
    "Team": "Oakland Athletics"
  },
  {
    "Name": "Casey",
    "Team": "Pittsburgh Pirates"
  },
  {
    "Name": "Drew",
    "Team": "Los Angeles Angels"
  },
  {
    "Name": "Daniel",
    "Team": "Washington Nationals"
  },
  {
    "Name": "Andrew",
    "Team": "Colorado Rockies"
  },
  {
    "Name": "Chris",
    "Team": "Chicago White Sox"
  }
]


owners = pd.DataFrame(data)

combined=owners.merge(wins, left_on='Team', right_on='Tm')
combined=combined[['Name','Team','W','L']]
combined['W']=combined['W'].astype(int)
combined=combined.sort_values('W', ascending=False)

summary=combined.groupby('Name')['W'].sum()
summary_sorted=summary.sort_values(ascending=False)
summary_df=pd.DataFrame(summary_sorted).reset_index()
summary_df= summary_df.rename(columns={"W":"Win Total"})
summary_df = summary_df.set_index('Name')


# In[22]:


# Define the prompt template
prompt_template = """Your name is DanBot and you are a slack bot. You are providing funny banter to your friends on the current in-progress standing of a competition to see who can pick the baseball teams that will win the most this season. Please analyze the data and provide banter with funny insights, make sure to give whoever is in last place a hard time. Throw in historical baseball facts when necessary. Always add a title 'DanBot's Daily Diamond Digs' to your message and begin the message with a quirky introduction. Here are the overall standings: {summary} and here are the details by team and owner:{results}"""

# Create the prompt template
prompt = PromptTemplate(template=prompt_template, input_variables=["summary","results"])

# Create the chain
llm = ChatAnthropic(model='claude-3-opus-20240229', temperature=0.9, anthropic_api_key = 'your api key')
chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain
friendly_banter = chain.run(summary=summary_df, results=combined)

slack_token='your slack token'
channel='mlb'

#publish to slack    
def push_to_slack(filename, df, slack_token, channel, title, initial_comment):    
    
    #app = App(token=slack_token)
    client = WebClient(token=slack_token)
    response = client.chat_postMessage(
                channel=channel,
                text="{} MLB Wins League Standings:".format(today) + f"```{summary_df}```"
            ,        mrkdwn=True
        )

    df.to_csv(filename, index=False)

    client = WebClient(token=slack_token)
    
    response = client.files_upload(
            channels=channel,
            file=filename,
            title=title,
            initial_comment=initial_comment
        )

push_to_slack(filename='MLB Records.csv', df=combined, slack_token=slack_token, channel=channel, title='MLB Records', initial_comment= friendly_banter)

