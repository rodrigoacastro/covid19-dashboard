from selenium import webdriver
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.metrics import r2_score
from datetime import datetime
import re
import os

class DataFetcher:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.binary_location = os.environ.get("GOOGLE_CHROME_BINARY")
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.executable_path=os.environ.get("CHROMEDRIVER_PATH")
        self.driver_wom, self.driver_g1, self.places = self.set_drivers()
   
    @st.cache(allow_output_mutation=True)
    def set_drivers(self):
        driver_wom = webdriver.Chrome(executable_path=self.executable_path, chrome_options=self.options)
        driver_wom.get('https://www.worldometers.info/coronavirus/country/brazil/')
        driver_wom.implicitly_wait(3)

        driver_g1 = webdriver.Chrome(executable_path=self.executable_path, chrome_options=self.options)
        driver_g1.get('https://especiais.g1.globo.com/bemestar/coronavirus/mapa-coronavirus/')
        driver_g1.implicitly_wait(5)

        places = [element.text for element in driver_g1.find_elements_by_class_name('places__cell')][2::]

        return driver_wom, driver_g1, places

    def get_count_numbers(self):
        count_numbers = self.driver_wom.find_elements_by_xpath('//*[@id="maincounter-wrap"]/div')
        main_counters = [element.text for element in count_numbers]
        total_cases = main_counters[0]
        total_deaths = main_counters[1]
        total_recovers = main_counters[2]
        
        return total_cases, total_deaths, total_recovers

    def get_daily_cases(self):
        script = self.driver_wom.find_element_by_xpath('/html/body/div[4]/div[2]/div[1]/div[2]/div/script')
        text = script.get_attribute('text')
        
        pattern_categories = r'(categories: \[.*\])'
        pattern_days = r'(\".*\")'
        pattern_data = r'(data: \[.*\])'

        days_list = re.findall(pattern_categories, text)[0]
        days = re.findall(pattern_days, days_list)

        date_list = days[0].split(",")
        
        data = re.findall(pattern_data, text)[0]

        list_daily_cases = data[7:][:-11].split(",")
        df_daily = pd.DataFrame({'date': date_list, 'cases': list_daily_cases})
        df_daily = df_daily.applymap(lambda x: x.replace('"', ''))
        df_daily['cases'] = df_daily['cases'].replace('null', 0)
        df_daily['cases'] = df_daily['cases'].astype('int64')
        if 'Feb 29' in df_daily['date'].values:
            df_daily = df_daily[df_daily['date'] != 'Feb 29']
        df_daily['datetime_obj'] = [datetime.strptime(x, '%b %d').replace(year=2020) for x in df_daily['date']]
        
        return df_daily

    def get_total_cases(self):
        script_total = self.driver_wom.find_element_by_xpath('/html/body/div[4]/div[2]/div[1]/div[1]/div/script')
        text = script_total.get_attribute('text')
        
        pattern_categories = '(categories: \[.*\])'
        pattern_days = r'(\".*\")'
        pattern_data = r'(data: \[.*\])'
        
        days_list = re.findall(pattern_categories, text)[0]
        days = re.findall(pattern_days, days_list)
        date_list = days[0].split(",")
        
        data = re.findall(pattern_data, text)[0]

        list_total_cases = data[7:][:-11].split(",")
        
        df_totalcases = pd.DataFrame({'date': date_list, 'cases': list_total_cases})
        df_totalcases = df_totalcases.applymap(lambda x: x.replace('"', ''))
        df_totalcases['cases'] = df_totalcases['cases'].astype('int64')
        
        # Drop Feb 29 to avoid bug on converting to datetime object
        if 'Feb 29' in df_totalcases['date'].values:
            df_totalcases = df_totalcases[df_totalcases['date'] != 'Feb 29']
        df_totalcases['datetime_obj'] = [datetime.strptime(x, '%b %d').replace(year=2020) for x in df_totalcases['date']]
        
        return df_totalcases

    def get_update_time(self):
        update_time = [element.text for element in self.driver_g1.find_elements_by_class_name('update__text')][0]
        pattern_date = r'(\d+/\d+/\d+)'
        pattern_time = r'(\d+:\d+)'

        date = re.findall(pattern_date, update_time)
        time = re.findall(pattern_time, update_time)

        return date[0], time[0]

    def get_cases_by_city(self):
        places = self.places
        locations = places[0::2]
        no_of_cases = places[1::2]

        location_cases_df = pd.DataFrame({'Cidade': locations, 'Número de casos': no_of_cases})
        location_cases_df['Número de casos'] = location_cases_df['Número de casos'].astype('int64')
        
        return location_cases_df

    def get_cases_by_state(self):
        state_cases = self.get_cases_by_city()
        state_cases = state_cases[state_cases['Cidade'] != 'Não informado']
        state_cases_sum = pd.DataFrame({'Estado': state_cases['Cidade'].map(lambda x: x[-2:]), 
                                        'Casos': state_cases['Número de casos']})
        state_cases_sum = state_cases_sum.groupby(by='Estado').sum().reset_index()
        state_cases_sum.sort_values(by='Casos', ascending=False, inplace=True)

        return state_cases_sum

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

        cases_state = self.get_cases_by_state()
        list_states = [state for state in coord_dict.keys()]
        lat_coords = [coord[0] for coord in coord_dict.values()]
        long_coords = [coord[1] for coord in coord_dict.values()]
        coord_df = pd.DataFrame({'state': list_states, 'lat': lat_coords, 'long': long_coords})
        coord_states_cases = pd.merge(coord_df, cases_state, how='inner', left_on='state', right_on='Estado')
        coord_states_cases['hover_text'] = coord_states_cases.apply(lambda row: row.state + ': ' + str(row.Casos), axis=1)

        api_key = 'pk.eyJ1IjoiYWxleG1hZ25vIiwiYSI6ImNrODU5d2pveDA0b28zaW95a2p6cHhydnAifQ.YiOEJwtD28loQ2d4txK6dg'

        fig = go.Figure(go.Scattermapbox(lat=coord_states_cases['lat'], lon=coord_states_cases['long'],
                                         mode='markers', 
                                         marker=go.scattermapbox.Marker(size=coord_states_cases['Casos']/10), 
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
