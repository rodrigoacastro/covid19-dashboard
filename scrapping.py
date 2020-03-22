from selenium import webdriver
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

class DataFetcher:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get('https://especiais.g1.globo.com/bemestar/coronavirus/mapa-coronavirus/')
        self.driver.implicitly_wait(10)

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