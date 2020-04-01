import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

class DataFetcher:
    def __init__(self):
        self.url_brazil_general = 'https://covid19-brazil-api.now.sh/api/report/v1/brazil/'
        self.url_brazil_states = 'https://covid19-brazil-api.now.sh/api/report/v1'
        self.url_world_cases = 'https://pomber.github.io/covid19/timeseries.json'
        
        self.brazil_general_json = requests.get(self.url_brazil_general).json()
        self.brazil_states_json = requests.get(self.url_brazil_states).json()
        self.world_cases_json = requests.get(self.url_world_cases).json()
        
    def get_apis_status_code(self):
        brazil_general = requests.get(self.url_brazil_general).status_code
        brazil_states = requests.get(self.url_brazil_states).status_code
        world_cases = requests.get(self.url_world_cases).status_code
        
        return brazil_general, brazil_states, world_cases
    
    def get_main_counters(self):
        brazil_counters = self.brazil_general_json
        confirmed = brazil_counters['data']['confirmed']
        deaths = brazil_counters['data']['deaths']
        recovered = brazil_counters['data']['recovered']
        
        return confirmed, deaths, recovered
    
    def get_update_time(self):
        update_time = self.brazil_general_json['data']['updated_at']
        update_time_brazil = pd.to_datetime(update_time) - pd.Timedelta(hours=3)
        date = str(update_time_brazil.day) + '/' + str(update_time_brazil.month) + '/' + str(update_time_brazil.year)
        time = str(update_time_brazil.hour) + 'hrs'
        
        return date, time
    
    def get_cases_timeline(self):
        dates = []
        confirmed = []
        deaths = []
        for day in self.world_cases_json['Brazil']:
            dates.append(day['date'])
            confirmed.append(day['confirmed'])
            deaths.append(day['deaths'])
            
        cases_df = pd.DataFrame({'date': dates, 'confirmed': confirmed, 'deaths': deaths})
        cases_df['date'] = pd.to_datetime(cases_df['date'])
        cases_df = cases_df[cases_df['date'] >= pd.to_datetime('2020-02-15')]
        cases_df['daily'] = cases_df['confirmed'] - cases_df['confirmed'].shift(1)
        
        return cases_df
    
    def get_state_cases(self):
        state_name = []
        states_sigla = []
        cases = []
        deaths = []
        for state in self.brazil_states_json['data']:
            state_name.append(state['state'])
            states_sigla.append(state['uf'])
            cases.append(state['cases'])
            deaths.append(state['deaths'])
            
        states_table = pd.DataFrame({'Estado': state_name, 'Casos Confirmados': cases, 'Mortes': deaths})
        states_table['Letalidade'] = np.round((states_table['Mortes'] / states_table['Casos Confirmados'])*100, 2)
        states_table['Letalidade'] = states_table['Letalidade'].map(lambda x: str(x) + '%')
        
        siglas_df = pd.DataFrame({'uf': states_sigla, 'cases': cases})
        
        return states_table, siglas_df

    def get_states_cases_plot(self):
        coord_dict = {
                      'AC': [ -8.77, -70.55]
                    , 'AL': [ -9.71, -35.73]
                    , 'AM': [ -3.07, -61.66]
                    , 'AP': [  1.41, -51.77]
                    , 'BA': [-12.96, -38.51]
                    , 'CE': [ -3.71, -38.54]
                    , 'DF': [-15.83, -47.86]
                    , 'ES': [-19.19, -40.34]
                    , 'GO': [-16.64, -49.31]
                    , 'MA': [ -2.55, -44.30]
                    , 'MT': [-12.64, -55.42]
                    , 'MS': [-20.51, -54.54]
                    , 'MG': [-18.10, -44.38]
                    , 'PA': [ -5.53, -52.29]
                    , 'PB': [ -7.06, -35.55]
                    , 'PR': [-24.89, -51.55]
                    , 'PE': [ -8.28, -35.07]
                    , 'PI': [ -8.28, -43.68]
                    , 'RJ': [-22.84, -43.15]
                    , 'RN': [ -5.22, -36.52]
                    , 'RO': [-11.22, -62.80]
                    , 'RS': [-30.01, -51.22]
                    , 'RR': [  1.89, -61.22]
                    , 'SC': [-27.33, -49.44]
                    , 'SE': [-10.90, -37.07]
                    , 'SP': [-23.55, -46.64]
                    , 'TO': [-10.25, -48.25]
                    }

        _, siglas_df = self.get_state_cases()
        list_states = [state for state in coord_dict.keys()]
        lat_coords = [coord[0] for coord in coord_dict.values()]
        long_coords = [coord[1] for coord in coord_dict.values()]
        coord_df = pd.DataFrame({'state': list_states, 'lat': lat_coords, 'long': long_coords})
        coord_states_cases = pd.merge(coord_df, siglas_df, how='inner', left_on='state', right_on='uf')
        coord_states_cases['hover_text'] = coord_states_cases.apply(lambda row: row.state + ': ' + str(row.cases), axis=1)

        api_key = 'pk.eyJ1IjoiYWxleG1hZ25vIiwiYSI6ImNrODU5d2pveDA0b28zaW95a2p6cHhydnAifQ.YiOEJwtD28loQ2d4txK6dg'

        fig = go.Figure(go.Scattermapbox(lat=coord_states_cases['lat'], lon=coord_states_cases['long'],
                                         mode='markers', 
                                         marker=go.scattermapbox.Marker(size=coord_states_cases['cases']/30), 
                                         text=coord_states_cases['hover_text'], 
                                         hoverinfo='text')
                                         )

        fig.update_layout(title={'text':'<b>Total de casos por estado</b><br>(Explore com o mouse)', 
                                         'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'
                                         }, 
                          autosize=True, 
                          hovermode='closest', 
                          mapbox=dict(accesstoken=api_key, bearing=0, center=dict(lat=-15,lon=-55),
                                      pitch=5, zoom=2.5),
                                )

        return fig
