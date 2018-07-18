import csv
from math import sqrt
import numpy as np
import pandas as pd
import os
from collections import OrderedDict


class Player(object):
    def __init__(self, team):
        self.team_id = team
        self.score = 0
        self.active = True

def get_lineups(game, period, dict):
    for p in dict:
        dict[p].active = False
    with open('Game_Lineup_Data.csv') as lineups:
        play_rows = list(csv.DictReader(lineups))
        for row in play_rows:
            if row["Game_id"] == game and row["Period"] == period:
                if row["Person_id"] not in dict:
                    dict[row["Person_id"]] = Player(row["Team_id"])
                dict[row["Person_id"]].active = True
    return dict

def update_points(points, team, dict):
    for p in dict:
        if dict[p].active:
            dict[p].score += points if team == dict[p].team_id else -points

def substitute(player1, player2, team, dict):
    dict[player1].active = False
    if player2 not in dict:
        dict[player2] = Player(team)
    dict[player2].active = True

def parse_quarter(game, period, dict):
    dict = get_lineups(game, period, dict)
    with open('Play_By_Play.csv') as plays:
        play_rows = list(csv.DictReader(plays))
        for row in play_rows:
            if row["Game_id"] == game and row["Period"] == period:
                global ft_ongoing
                if row["Event_Msg_Type"] == '6' and int(row["Option3"]) > 0:
                    ft_ongoing = True
                elif row["Event_Msg_Type"] == '1' or row["Event_Msg_Type"] == '3':
                    if row["Option1"] != '0':
                        points = int(row["Option1"])
                        update_points(points, row["Team_id"], dict)
                    if row["Event_Msg_Type"] == '3' and (int(row["Action_Type"]) in end_ft):
                        ft_ongoing = False
                        sub_all(sub_dict, row["Team_id"], dict)
                        sub_dict.clear()
                elif row["Event_Msg_Type"] == '8':
                    if ft_ongoing:
                        sub_dict[row["Person1"]] = row["Person2"]
                    else:
                        substitute(row["Person1"], row["Person2"], row["Team_id"], dict)

def sub_all(sub_dict, team, dict):
    if not sub_dict:
        return
    for player_out in sub_dict:
        player_in = sub_dict[player_out]
        substitute(player_out, player_in, team, dict)

ft_ongoing = False
#keys going out of game, value going into the game
sub_dict = {}
#Action Type for the last free throw of any series
end_ft = [10, 12, 15, 26, 20, 19, 22]

def saver(dict, game):
    final = open('BigBallerPredictions_Q1_BBALL.csv', 'a')
    for each in dict:
        row_to_add = "%s,  %s, %s\n" % (game, each, dict[each].score)
        final.write(row_to_add)
    final.close


def parse_game(game):
    dict = {}
    parse_quarter(game, '1', dict)
    parse_quarter(game, '2',  dict)
    parse_quarter(game, '3', dict)
    parse_quarter(game, '4', dict)
    parse_quarter(game, '5', dict)
    saver(dict, game)

def parse_file():
    game_set = set()
    with open('Play_By_Play.csv') as action:
        action_events = list(csv.DictReader(action))
    for row in action_events:
        game = row["Game_id"]
        if game not in game_set:
            game_set.add(game)
            parse_game(game)

final = open('BigBallerPredictions_Q1_BBALL.csv', 'a')
final.write('Game_ID, Player_ID, Player_Plus/Minus')
parse_file()
