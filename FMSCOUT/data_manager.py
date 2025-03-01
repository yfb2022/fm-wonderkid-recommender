# data_manager.py

import pandas as pd
from ast import literal_eval
from FMSCOUT.skill_calculator import FieldPlayerSkillCalculator
from FMSCOUT.skill_calculator import GKSkillCalculator
from pathlib import Path

class DataManager:
    def __init__(self):
        data_path = "https://raw.githubusercontent.com/yfb2022/fm-wonderkid-recommender/refs/heads/master/data/"
        self.rest_df_scl = pd.read_csv(data_path + 'rest_df_scl.csv')
        self.rest_df = pd.read_csv(data_path + 'rest_df.csv')
        self.GK_df_scl = pd.read_csv(data_path + 'GK_df_scl.csv')
        self.GK_df = pd.read_csv(data_path + 'GK_df.csv')

        self.rest_df.loc[self.rest_df['pics'] == 'None', 'pics'] = (
            'https://img.a.transfermarkt.technology/portrait/header/default.jpg?lm=1'
        )
        self.GK_df.loc[self.GK_df['pics'] == 'None', 'pics'] = (
            'https://img.a.transfermarkt.technology/portrait/header/default.jpg?lm=1'
        )
        for df in [self.rest_df_scl, self.GK_df_scl]:
            df['cluster'] = df['cluster'].apply(lambda x: literal_eval(x))

    def get_player_data(self, player_name: str):
        if player_name in self.rest_df['Name'].values:
            temp_df = self.rest_df.copy()
            temp_df_scl = self.rest_df_scl.copy()
            categories = ['Defending', 'Physical', 'Speed', 'Vision', 'Attacking', 'Technique', 'Aerial', 'Mental']
            skill_calc = FieldPlayerSkillCalculator()
        elif player_name in self.GK_df['Name'].values:
            temp_df = self.GK_df.copy()
            temp_df_scl = self.GK_df_scl.copy()
            categories = ['Distribution', 'Eccentricity', 'Mental', 'Shot Stopping', 'Physical', 'Speed', 'Aerial',
                          'Communication']
            skill_calc = GKSkillCalculator()
        else:
            raise ValueError("선수 이름이 올바르지 않습니다.")

        return temp_df, temp_df_scl, categories, skill_calc

    def get_all_player_names(self):
        names = self.rest_df['Name'].to_list() + self.GK_df['Name'].to_list()
        names.append('')
        return names
