from src.elopy import *
import streamlit as st

def calculate(df, player_list):
  """
  Calculate the elo ratings of matches listed on an Excel spreadsheet starting from top to bottom.
  The first row should be a header with labels for date, player 1, player 1 score, player 2, and player 2 score, in that order.
  parameters:
    file: location of the Excel file as a string
  """

  i = Implementation(player_list)

  total_rows = len(df)

  for r in range(total_rows):
    player1_name = df.loc[r]['Player 1']
    player2_name = df.loc[r]['Player 2']
    #try to add players to the list
    #if they already exist this will do nothing
    i.addPlayer(player1_name)
    i.addPlayer(player2_name)
    player1_score = df.loc[r]['Score 1']
    player2_score = df.loc[r]['Score 2']
    if player1_score > player2_score:
      i.recordMatch(player1_name, player2_name, winner = player1_name)
    elif player1_score < player2_score:
      i.recordMatch(player1_name, player2_name, winner = player2_name)
    else:
      i.recordMatch(player1_name, player2_name, draw = True)

  return i