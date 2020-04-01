from scrapping import DataFetcher
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

class Models:
    def __init__(self):
        self.datafetcher_obj = DataFetcher()

    def get_exponential_predictions(self):
        cases_last_20days = self.datafetcher_obj.get_cases_timeline().iloc[-20:]
        cases_last_20days['log_cases'] = np.log(cases_last_20days['confirmed'])

        # Fitting log curve
        x = np.arange(20)
        y = cases_last_20days['log_cases']
        fitted_params = np.polyfit(x, y, 1)
        predictions_log = [day*fitted_params[0] + fitted_params[1] for day in np.arange(27)]

        # Generating timeseries for 7 days ahead, and appending with the prediction time
        days_7_days_ahed = pd.date_range(cases_last_20days['date'].values[-1], 
                                        cases_last_20days['date'].values[-1] + pd.Timedelta(7, unit='D'))
        days_pred = cases_last_20days['date'][-20:-1].append(pd.Series(days_7_days_ahed))

        # DataFrame with predictions
        prediction_df = pd.DataFrame({'date': days_pred, 'pred_cases': np.exp(predictions_log)})

        # Calculate coefficient of determination of fitting
        r2 = np.round(r2_score(cases_last_20days['log_cases'], predictions_log[:20]), 3)

        return cases_last_20days, prediction_df, r2

    def get_polinomial_predictions(self):
        cases_last_20days = self.datafetcher_obj.get_cases_timeline().iloc[-20:]

        # Fitting poli curve
        x = np.arange(20)
        y = cases_last_20days['confirmed']
        fitted_params = np.polyfit(x, y, 3)
        predictions = [fitted_params[3] + day*fitted_params[2] + (day**2)*fitted_params[1] + (day**3)*fitted_params[0] for day in np.arange(27)]

        # Generating timeseries for 7 days ahead, and appending with the prediction time
        days_7_days_ahed = pd.date_range(cases_last_20days['date'].values[-1], 
                                        cases_last_20days['date'].values[-1] + pd.Timedelta(7, unit='D'))
        days_pred = cases_last_20days['date'][-20:-1].append(pd.Series(days_7_days_ahed))

        # DataFrame with predictions
        prediction_df = pd.DataFrame({'date': days_pred, 'pred_cases': predictions})

        return prediction_df
