import streamlit as st
import numpy as np 
import pandas as pd
import plotly.graph_objects as go
from scrapping import DataFetcher

st.title('Covid-19 dashboard')

st.write('Bem-vindo ao dashboard de acompanhamento de casos do Coronavírus no Brasil.')
st.write('Os dados apresentados aqui são coletados a partir de um webscrapping de um site da GloboNews.\
          A escolha da fonte foi feita visando a confiabilidade da informação.')

st.write('Utilize o menu ao lado para fazer a navegação.')

actions = ['Situação atual', 'Previsões']
choice = st.sidebar.selectbox('Selecione uma opção', actions)

webscrapping = DataFetcher()

if choice == 'Situação atual':
    cases_df = webscrapping.cases_per_day

    fig_daily_cases = go.Figure(data=go.Bar(x=cases_df['date'], y=cases_df['no_cases']))

    fig_daily_cases.update_layout(title='<b>Novos casos por dia</b>',
                                xaxis_title='Dia',
                                yaxis_title='Novos casos confirmados')

    st.plotly_chart(fig_daily_cases)

    fig_cumulative_cases = go.Figure(data=go.Scatter(x=cases_df['date'], y=cases_df['cases_cumsum'], 
                                    line=dict(color='firebrick', width=4), 
                                    mode='lines+markers', marker=dict(size=10)))

    fig_cumulative_cases.update_layout(title='<b>Total de casos por dia</b>', xaxis_title='Dia', yaxis_title='Casos totais')

    st.plotly_chart(fig_cumulative_cases)

if choice == 'Previsões':
    cases_last_10days = webscrapping.cases_last_10days
    predictions = webscrapping.predictions
    cases_df = webscrapping.cases_per_day

    # Quality of last 10 days fitting to exponential model plot
    fig_quality = go.Figure()
    fig_quality.add_trace(go.Scatter(x=cases_last_10days['date'], y=cases_last_10days['log_cumsum'], line=dict(color='firebrick', width=4),
                    mode='lines+markers', marker=dict(size=10), name='Real'))
    fig_quality.add_trace(go.Scatter(x=cases_last_10days['date'], y=np.log(predictions['pred_cases']), name='Ajustado'))

    fig_quality.update_layout(title='<b>Qualidade do ajuste exponencial em janela de 10 dias</b>',
                    xaxis_title='Dia',
                    yaxis_title='log dos casos totais')

    st.plotly_chart(fig_quality)

    # Number of cases with predictions plot 
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=cases_df['date'], y=cases_df['cases_cumsum'], line=dict(color='#7f7f7f', width=4),
                    mode='lines+markers', marker=dict(size=10), name='Dados'))
    fig_pred.add_trace(go.Scatter(x=predictions['date'], y=predictions['pred_cases'], name='Ajuste', line=dict(color='red')))

    fig_pred.update_layout(title='<b>Ajsute exponencial com previsão para os próximos 7 dias</b>',
                    xaxis_title='Dia',
                    yaxis_title='Casos totais')

    st.plotly_chart(fig_pred)
