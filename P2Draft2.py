# P2Draft2

import json, re, requests, math, csv
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from pprint import pprint


# Section 1 --> Web Scraping

def clean_webscrape():
    response = requests.get('https://en.wikipedia.org/wiki/Forbes_list_of_the_most_valuable_NFL_teams')
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('table', {'class': 'wikitable'})
    ranking_table = rows[0]
    composition_table = rows[1]
    valuation_table = rows[2]

    teams_list = []
    for row in ranking_table.find_all('tr')[1:]:
        content = row.find_all('td')
        rank = int(content[0].text.strip()[1:])
        rank_change = int(content[1].text.strip()) if content[1].text.strip() != '' else 0
        if content[1].find('span').find('span')['title'] == 'Decrease':
            rank_change *= -1
        team = content[2].text.strip()
        state = content[3].text.strip()
        value = float(re.search(r'\$(.+?)\s',content[4].text.strip()).group(1))
        value_change = int(content[5].text.strip()[:-1])
        percent_debt = content[6].text.strip()
        revenue = content[7].text.strip()
        operating_income = content[8].text.strip()
        teams_list.append([team,rank,value_change,rank_change,value])

    best_teams_financially = sorted(teams_list,key=lambda x:(-x[3],-x[2],x[0]))


    teams_list_2 = []
    for row in composition_table.find_all('tr')[1:]:
        content = row.find_all('td')
        sport_value = float(re.search(r'\$(.+?)\s',content[2].text.strip()).group(1))
        market_value = float(re.search(r'\$(.+?)\s',content[3].text.strip()).group(1))
        stadium_value = float(re.search(r'\$(.+?)\s',content[4].text.strip()).group(1))
        brand_value = float(re.search(r'\$(.+?)\s',content[5].text.strip()).group(1))
        teams_list_2.append([sport_value,market_value,stadium_value,brand_value])


    teams_list_3 = []
    for row in valuation_table.find_all('tr')[1:]:
        content = row.find_all('td')
        eval2021 = int(content[1].text.strip()) if ',' not in content[1].text.strip() else int(content[1].text.strip().split(',')[0] + content[1].text.strip().split(',')[1])
        eval2020 = int(content[2].text.strip()) if ',' not in content[2].text.strip() else int(content[2].text.strip().split(',')[0] + content[2].text.strip().split(',')[1])
        eval2019 = int(content[3].text.strip()) if ',' not in content[3].text.strip() else int(content[3].text.strip().split(',')[0] + content[3].text.strip().split(',')[1])
        eval2018 = int(content[4].text.strip()) if ',' not in content[4].text.strip() else int(content[4].text.strip().split(',')[0] + content[4].text.strip().split(',')[1])
        eval2017 = int(content[5].text.strip()) if ',' not in content[5].text.strip() else int(content[5].text.strip().split(',')[0] + content[5].text.strip().split(',')[1])
        eval2016 = int(content[6].text.strip()) if ',' not in content[6].text.strip() else int(content[6].text.strip().split(',')[0] + content[6].text.strip().split(',')[1])
        eval2015 = int(content[7].text.strip()) if ',' not in content[7].text.strip() else int(content[7].text.strip().split(',')[0] + content[7].text.strip().split(',')[1])
        eval2014 = int(content[8].text.strip()) if ',' not in content[8].text.strip() else int(content[8].text.strip().split(',')[0] + content[8].text.strip().split(',')[1])
        eval2013 = int(content[9].text.strip()) if ',' not in content[9].text.strip() else int(content[9].text.strip().split(',')[0] + content[9].text.strip().split(',')[1])
        eval2012 = int(content[10].text.strip()) if ',' not in content[10].text.strip() else int(content[10].text.strip().split(',')[0] + content[10].text.strip().split(',')[1])
        teams_list_3.append([eval2016/1000,eval2021/1000])


    teams_acronym = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']
    complete_team_list = []
    for i,team in enumerate(teams_list):
        complete_team_list.append(team + teams_list_2[i] + teams_list_3[i])

    final_list = sorted(complete_team_list,key=lambda x:x[0])
    final_list_fr = []
    for i,team in enumerate(final_list):
        final_list_fr.append([teams_acronym[i]] + final_list[i][1:])


    final_list_fr = [['team','rank','pct_value_inc','rank_change','total_value','sport_value','market_value','stadium_value','brand_value','2016_valuation','2021_valuation']] + final_list_fr

    with open('cleaned_webscrape.csv','w', newline = '') as outfile:
        writer = csv.writer(outfile)
        for line in final_list_fr:
            writer.writerow(line)

    return final_list_fr

# clean_webscrape()

# Section 2 --> API

def clean_api():

    base = "https://www.fantasyfootballdatapros.com/api/players/"
    # add year/week to get fantasy stats for all players in a given week

    pairs = [(year,week) for year in range(2016,2020) for week in range(1,18)]


    great_performances = []
    t_list = []
    for item in pairs:
        r = requests.get(base + str(item[0]) + '/' + str(item[1]))
        data = r.json()

        for player in data:



            # ONLY CONSIDERING GREAT FANTASY PERFORMANCES

            if player['fantasy_points']['ppr'] >= 30:


                # NAMING VARIABLES FROM JSON DICT
                year = item[0]
                week = item[1]
                points = round(player['fantasy_points']['ppr'] ,2)
                name = player['player_name']
                position = player['position']
                team = player['team']
                pass_pts = round(-2*player['stats']['passing']['int'] + 6*player['stats']['passing']['passing_td'] + .04*player['stats']['passing']['passing_yds'],2)
                receive_pts = round(player['stats']['receiving']['receptions'] + .1*player['stats']['receiving']['receiving_yds'] + 6*player['stats']['receiving']['receiving_td'],1)
                rush_pts = round(.1*player['stats']['rushing']['rushing_yds'] + 6*player['stats']['rushing']['rushing_td'],1)



                # CHANGING TEAM ABBREVIATIONS TO BE STANDARDIZED

                if team == "GNB":
                    team = 'GB'
                elif team == 'KAN':
                    team = 'KC'
                elif team == 'NOR':
                    team = 'NO'
                elif team == 'NWE':
                    team = 'NE'
                elif team == 'OAK':
                    team = 'LV'
                elif team == 'SDG':
                    team = 'LAC'
                elif team == 'SFO':
                    team = 'SF'
                elif team == 'TAM':
                    team = 'TB'



                # ACCOUNTING FOR FUMBLES BASED ON POSITION

                if player['position'] == 'WR' or player['position'] == 'TE':
                    receive_pts -= 2*player['fumbles_lost']
                else:
                    rush_pts -= 2*player['fumbles_lost']



                # STANDARDIZING POSITIONS

                if position == 'FB' or position == 'HB':
                    position = 'RB'



                # ADDING PLAYER INFO TO COMBINED LIST OF PERFORMANCES

                great_performances.append([name,position,team,points,pass_pts,receive_pts,rush_pts,year,week])



    # ADDING TAG BASED ON POINTS

    fantasy_performance_list = []

    for player in great_performances:
        if player[3] >= 50:
            fantasy_performance_list.append(player[:3] + ['legendary'] + player[3:])
        elif player[3] >= 40:
            fantasy_performance_list.append(player[:3] + ['amazing'] + player[3:])
        else:
            fantasy_performance_list.append(player[:3] + ['great'] + player[3:])


    fantasy_performance_list = [['name','position','team','performance_quality','total_points','passing_points','receiving_points','rushing_points','year','week']] + fantasy_performance_list

    with open('cleaned_api.csv','w', newline = '') as outfile:
        writer = csv.writer(outfile)
        for line in fantasy_performance_list:
            writer.writerow(line)

    return fantasy_performance_list

# clean_api()


# Section 3 --> CSV Cleaning



def clean_csv():
    final_final_list=[]
    for num in range(6,10):
        with open('pbp-201' + str(num) + '.csv', 'r') as f:
            reader = csv.reader(f)
            reader_list = list(reader)

        header = reader_list[0]
        data = reader_list[1:]

        old_teams_acronym = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC','LA','LV', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS','SD']
        new_teams_acronym = old_teams_acronym[:-1] + ['LAC']
        team_penalty_dict = {}
        team_game_dates = []
        team_fd_dict = {}
        team_touchdown_dict = {}
        team_3down_dict = {}
        team_4down_dict = {}
        year = '201' + str(num)


        for line in data:


            # NAMING VARIABLES FROM CSV FILE

            date = line[1]
            offense_team = line[5]
            defense_team = line[6]
            fd_play = line[11]
            play_description = line[14]
            play_type = line[21]
            is_touchdown = line[-20]
            penalty_team = line[-4]
            is_penalty_accepted = line[-5]
            penalty_yds = line[-1]
            down = line[7]
            is_noplay = line[-3]
            yds_to_go = line[8]


            if down == '3' and is_noplay == '0':
                if offense_team in team_3down_dict:
                    team_3down_dict[offense_team] = [team_3down_dict[offense_team][0],team_3down_dict[offense_team][1]+1]
                else:
                    team_3down_dict[offense_team] = [0,1]

            if down == '4' and is_noplay == '0' and 'PUNT' not in play_type and 'FIELD GOAL' not in play_type:
                if offense_team in team_4down_dict:
                    team_4down_dict[offense_team] = [team_4down_dict[offense_team][0],team_4down_dict[offense_team][1]+1]
                else:
                    team_4down_dict[offense_team] = [0,1]


            # FIRST DOWN, NOT INCLUDING PENALTY FIRST DOWNS

            if fd_play != '0':
                if 'EXTRA POINT' not in play_type and 'TWO-POINT' not in play_type and 'KICK OFF' not in play_type and 'TIMEOUT' not in play_type and 'END QUARTER' not in play_type:
                    if offense_team in team_fd_dict:
                        team_fd_dict[offense_team] += 1
                    else:
                        team_fd_dict[offense_team] = 1


                    # ADDING TO DOWN DICTIONARIES

                    if down == '3' and 'REVERSED' not in play_description and is_noplay == '0' or down == '3' and is_penalty_accepted == '1' and penalty_team == defense_team and int(penalty_yds) >= int(yds_to_go):
                        team_3down_dict[offense_team] = [team_3down_dict[offense_team][0]+1,team_3down_dict[offense_team][1]]


                    if down == '4' and 'REVERSED' not in play_description and is_noplay == '0' or down == '4' and 'REVERSED' not in play_description and is_noplay == '1' and is_penalty_accepted == '1' and penalty_team == defense_team and int(penalty_yds) >= int(yds_to_go):
                        team_4down_dict[offense_team] = [team_4down_dict[offense_team][0]+1,team_4down_dict[offense_team][1]]


                    # TOUCHDOWNS INFO

                    if is_touchdown == '1':
                        if 'INTERCEPTED' not in play_description and 'FUMBLE' not in play_description and 'REVERSED' not in play_description:
                            if line[5] in team_touchdown_dict:
                                team_touchdown_dict[offense_team] += 1
                            else:
                                team_touchdown_dict[offense_team] = 1
                        elif 'REVERSED' in play_description:
                            date = date
                        else:
                            if defense_team in team_touchdown_dict:
                                team_touchdown_dict[defense_team] += 1
                            else:
                                team_touchdown_dict[defense_team] = 1



            # PENALTY INFO

            if penalty_team == '' or is_penalty_accepted == '0':
                continue
            elif penalty_team in team_penalty_dict:
                team_penalty_dict[penalty_team] = (team_penalty_dict[penalty_team][0] + int(penalty_yds), team_penalty_dict[penalty_team][1] + 1)
            else:
                team_penalty_dict[penalty_team] = (int(penalty_yds), 1)



        final_info = []

        if int(year) <= 2016:
            for team in old_teams_acronym:
                team_info = [team,team_touchdown_dict[team],team_fd_dict[team],team_3down_dict[team],team_4down_dict[team],team_penalty_dict[team]] if team != 'LV' else [team,team_touchdown_dict[team],team_fd_dict[team],team_3down_dict[team],team_4down_dict[team],team_penalty_dict['OAK']]
                final_info.append(team_info)
        else:
            for team in new_teams_acronym:
                team_info = [team,team_touchdown_dict[team],team_fd_dict[team],team_3down_dict[team],team_4down_dict[team],team_penalty_dict[team]] if team != 'LV' else [team,team_touchdown_dict[team],team_fd_dict[team],team_3down_dict[team],team_4down_dict[team],team_penalty_dict['OAK']]
                final_info.append(team_info)

        for position,team_info in enumerate(final_info):
            if team_info[0] == 'SD':
                final_info[position][0] = 'LAC'
            elif team_info[0] == 'LA':
                final_info[position][0] = 'LAR'


        real_final_info = []
        for team in final_info:
            team_info = [team[0]] + [int(year)] + team[1:3] + [team[3][0]] + [team[3][1]] + [round(100*team[3][0]/team[3][1],2)] + [team[4][0]] + [team[4][1]] + [round(100*team[4][0]/team[4][1],2)] + [team[-1][1]] + [team[-1][0]] + [round(team[-1][0]/team[-1][1],2)]
            real_final_info.append(team_info)
        real_final_info = sorted(real_final_info,key = lambda x:x[0])
        final_final_list.append(real_final_info)



    final_final_list = [['team','year','touchdowns','first_downs','third_down_conversions','total_third_downs','third_down_conversion_rate','fourth_down_conversions','total_fourth_downs','fourth_down_conversion_rate','num_penalties','total_penalty_yds','yds_per_penalty']] + final_final_list[0] + final_final_list[1] + final_final_list[2] + final_final_list[3]

    with open('cleaned_pbp.csv','w', newline = '') as outfile:
        writer = csv.writer(outfile)
        for line in final_final_list:
            writer.writerow(line)

    return final_final_list

# clean_csv()

