import ast
import time
import pandas as pd
import streamlit as st
from google.cloud import firestore
from src.calculate import calculate

from dotenv import load_dotenv
from os import environ
load_dotenv()

#################################################################################################
# STREAMLIT CONFIG
#################################################################################################

#################################################################################################
# GET DATA
#################################################################################################
firestore_key = ast.literal_eval(environ['FIRESTORE_KEY'])
db = firestore.Client.from_service_account_info(firestore_key)

history_ref = db.collection('history')
history = [history_doc.to_dict() for history_doc in history_ref.stream()]
history_df = pd.DataFrame(history)
history_df = history_df[['Timestamp', 'Player 1', 'Score 1', 'Player 2', 'Score 2']]

if len(history_df) > 0:
  timezone = environ['TIMEZONE']
  history_df.loc[:,'Timestamp'] = pd.to_datetime(history_df['Timestamp'],unit='ms',utc=True)
  history_df.loc[:,'Timestamp'] = history_df['Timestamp'].dt.tz_convert(timezone).dt.tz_localize(None)
  history_df = history_df.sort_values(by=['Timestamp']).reset_index(drop=True)

players_ref = db.collection('players')
players = [players_doc.to_dict() for players_doc in players_ref.stream()]
players_df = pd.DataFrame(players).sort_values(by=['Name'])
player_name_list = players_df['Name'].to_list()

st.button('Refresh')
i = calculate(history_df)
ranking_tab, add_tab = st.tabs(['Rankings & Records', 'Add Records & Players'])
player_list = i.getPlayerList()

#################################################################################################
# RANKINGS & MATCH HISTORY
#################################################################################################
with ranking_tab:
  rating_df = pd.DataFrame(i.getRatingList(), columns=['Name', 'Rating'])

  # If players have no matches, give them default 1000 rating
  for player_name in players_df['Name'].to_list():
    if player_name not in rating_df['Name'].to_list():
      i.addPlayer(player_name, rating=0)

  rating_df = pd.DataFrame(i.getRatingList(), columns=['Name', 'Rating']).sort_values(by='Rating', ascending=False).reset_index(drop=True)
  rating_df.index += 1

  st.title('AsBuilt Table Tennis Rankings')
  st.write(rating_df)

  st.title('Match Records')

  if len(history_df) > 0:
    st.write(history_df.sort_values(by=['Timestamp'], ascending=False).reset_index(drop=True))
  else:
    st.write(history_df)

#################################################################################################
# RECORD MATCH
#################################################################################################
with add_tab:
  st.title('Add Match Records')

  with st.form('add_record'):
    player1_col, score1_col, player2_col, score2_col = st.columns(4)
    player1 = player1_col.selectbox('Select Player 1', player_name_list)
    score1 = score1_col.number_input('Enter Score 1', min_value=0, step=1)
    player2 = player2_col.selectbox('Select Player 2', player_name_list)
    score2 = score2_col.number_input('Enter Score 2', min_value=0, step=1)
    add_record = st.form_submit_button("Add Record")

    if add_record:
      if player1 == player2:
        st.error('Both players are the same')
      if score1 == 0 and score2 == 0:
        st.error('Both scores are 0')
      else:
        timeNow = time.time()*1000
        history_ref.add({"Timestamp":timeNow, "Player 1":player1, "Score 1":score1, "Player 2":player2, "Score 2":score2})
        st.info('Record Added')

  st.title('Add Player')

  with st.form('add_player'):
    player = st.text_input('Player Name', value='')
    add_player = st.form_submit_button("Add Player")

    if add_player:
      if player=='':
        st.error('Player name is empty')
      elif player.upper() in [name.upper() for name in players_df['Name']]:
        st.error('Player name already taken')
      else:
        players_ref.add({"Name":player})


