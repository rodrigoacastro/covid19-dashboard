from selenium import webdriver
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import re
import warnings
warnings.filterwarnings("ignore")

class DataFetcher:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get('https://especiais.g1.globo.com/bemestar/coronavirus/mapa-coronavirus/')
        self.driver.implicitly_wait(5)

        #Total cases
        self.total_cases = [element.text for element in self.driver.find_elements_by_class_name('cases-overview__total')][0]

        # Cases in time
        self.cases_date = self.driver.find_elements_by_class_name('cases-by-day__date')
        self.cases_number = self.driver.find_elements_by_class_name('cases-by-day__total')

        #Cases per day and last 10 days
        self.cases_per_day = self.get_cases_per_day()
        self.cases_last_10days = self.cases_per_day.iloc[-11:-1]

        # Predictions
        self.predictions = self.get_predictions()


    def get_cases_per_day(self):
        cases_date_list = []
        cases_total_list = []

        for element in self.cases_date:
            cases_date_list.append(element.text)
            
        for element in self.cases_number:
            cases_total_list.append(element.text)

        # Loading the lists into a dataframe
        cases_per_day = pd.DataFrame({'date': cases_date_list, 'no_cases': cases_total_list})

        # Data transformation
        cases_per_day.drop(cases_per_day.tail(2).index, inplace=True)
        cases_per_day['date'] = cases_per_day['date'] + '/2020'
        cases_per_day['date'] = pd.to_datetime(cases_per_day['date'], format='%d/%m/%Y')
        cases_per_day['no_cases'] = cases_per_day['no_cases'].astype('int64')

        cases_per_day.sort_values(by='date', ascending=True, inplace=True)

        # Create cumulative sum of number of cases

        cases_per_day['cases_cumsum'] = cases_per_day['no_cases'].cumsum()
        cases_per_day['log_cumsum'] = np.log(cases_per_day['cases_cumsum'])

        return cases_per_day

    def get_predictions(self):

        # Fitting log curve

        x = np.arange(10)
        y = self.cases_last_10days['log_cumsum']

        fitted_params = np.polyfit(x, y, 1)

        predictions_log = [day*fitted_params[0] + fitted_params[1] for day in np.arange(18)]

        # Generating timeseries for 7 days ahed, and appending with the prediction time
        days_7_days_ahed = pd.date_range(self.cases_per_day.date[0], self.cases_per_day.date[0] + pd.Timedelta(7, unit='D'))
        days_pred = self.cases_per_day['date'][-11:-1].append(pd.Series(days_7_days_ahed))

        # DataFrame with predictions
        prediction_df = pd.DataFrame({'date': days_pred, 'pred_cases': np.exp(predictions_log)})

        return prediction_df

    def get_update_time(self):
        update_time = [element.text for element in self.driver.find_elements_by_class_name('update__text')][0]
        pattern_date = r'(\d+/\d+/\d+)'
        pattern_time = r'(\d+:\d+)'

        date = re.findall(pattern_date, update_time)
        time = re.findall(pattern_time, update_time)

        return date[0], time[0]

    def get_cases_by_city(self):
        places = [element.text for element in self.driver.find_elements_by_class_name('places__cell')][2::]
        locations = places[0::2]
        no_of_cases = places[1::2]

        location_cases_df = pd.DataFrame({'Cidade': locations, 'Número de casos': no_of_cases})
        location_cases_df['Número de casos'] = location_cases_df['Número de casos'].astype('int64')

        location_cases_df.style.set_properties(subset=['Número de casos'], **{'width': '300px'})

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
                                         marker=go.scattermapbox.Marker(size=coord_states_cases['Casos']/8), 
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
