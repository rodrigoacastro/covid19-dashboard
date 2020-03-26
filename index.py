import streamlit as st
import numpy as np 
import pandas as pd
import plotly.graph_objects as go
from scrapping import DataFetcher

st.title('Covid-19 dashboard')

st.write('Bem-vindo ao dashboard de acompanhamento de casos do Coronavírus no Brasil.')
st.write('Os dados apresentados aqui são coletados a partir de um webscrapping de um site do G1 sobre o assunto.\
          A escolha da fonte foi feita visando a confiabilidade da informação.')

st.write('Utilize o menu ao lado para fazer a navegação.')

st.sidebar.title('Navegação')
actions = ['Situação atual', 'Previsões']
choice = st.sidebar.selectbox('Selecione uma opção', actions)

with st.spinner('Buscando dados...'):
    webscrapping = DataFetcher()

date, time = webscrapping.get_update_time()

st.text('')
st.text('')

st.write('<i>Dados atualizados em </i>', date, ' <i>às</i> ', time, unsafe_allow_html=True)

st.write('________________________________')

if choice == 'Situação atual':

    st.write('<b>Casos totais até o momento: </b>', webscrapping.total_cases, unsafe_allow_html=True)

    cases_df = webscrapping.cases_per_day

    fig_daily_cases = go.Figure(data=go.Bar(x=cases_df['date'], y=cases_df['no_cases']))

    fig_daily_cases.update_layout(title={'text':'<b>Novos casos por dia</b>', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
                                yaxis_title='Novos casos confirmados',
                                margin=dict(b=0, t=70))

    st.plotly_chart(fig_daily_cases, use_container_width=True)

    fig_cumulative_cases = go.Figure(data=go.Scatter(x=cases_df['date'], y=cases_df['cases_cumsum'], 
                                    line=dict(color='firebrick', width=4), 
                                    mode='lines+markers', marker=dict(size=10)))

    fig_cumulative_cases.update_layout(title={'text':'<b>Total de casos por dia</b>', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'}, 
                                       yaxis_title='Casos totais', 
                                       margin=dict(t=70))

    st.plotly_chart(fig_cumulative_cases, use_container_width=True)

    cases_by_city = webscrapping.get_cases_by_city()

    st.text('')
    st.header('Distribuição de casos por localidade')

    ### Using plotly table
    fig_cities_table = go.Figure(data=[go.Table(
                columnwidth = [600,600],
                header=dict(values=list(cases_by_city.columns),
                fill_color='lightblue',
                align='center'),
                cells=dict(values=[cases_by_city['Cidade'], cases_by_city['Número de casos']],
                    fill_color='lavender',
                    align='center')
                )
            ])

    fig_cities_table.update_layout(margin=dict(l=0, r=0, t=10, b=0))

    st.plotly_chart(fig_cities_table, use_container_width=True, config={'displayModeBar': False})

    fig_state_cases = webscrapping.get_states_cases_plot()

    st.plotly_chart(fig_state_cases, use_container_width=True)

if choice == 'Previsões':

    st.sidebar.title('Selecione o modelo')
    
    # Modelo auto-regressivo e SEIR necessitam de ser desenvolvidos!
    model = st.sidebar.radio('', ['Exponencial', 'Auto-regressivo', 'SEIR (Simulação)'])

    if model == 'Exponencial':
        st.markdown('## Modelo Exponencial')
        st.write('O modelo exponencial é indicado para modelar a epidemia nos seus estágios iniciais.')
        st.write('Contudo, a análise da adequação da curva de casos ao modelo exponencial nos informa a respeito das medidas de contenção que estão sendo adotadas.')
        st.write('Caso o ajuste ao modelo não seja satisfatório, significa que as medidas de contenção estão surtindo efeito em freiar a epidemia que, caso as medidas de contenção fossem inexistentes, teria seu número casos acompanhando a curva exponencial.')

        cases_last_10days = webscrapping.cases_last_10days
        predictions = webscrapping.predictions
        cases_df = webscrapping.cases_per_day

        # Quality of last 10 days fitting to exponential model plot
        fig_quality = go.Figure()
        fig_quality.add_trace(go.Scatter(x=cases_last_10days['date'], y=cases_last_10days['log_cumsum'], line=dict(color='firebrick', width=4),
                        mode='lines+markers', marker=dict(size=10), name='Real'))
        fig_quality.add_trace(go.Scatter(x=cases_last_10days['date'], y=np.log(predictions['pred_cases']), name='Ajustado'))

        fig_quality.update_layout(title='<b>Qualidade do ajuste exponencial em janela de 10 dias</b>',
                                  yaxis_title='log (casos totais)')

        st.plotly_chart(fig_quality)

        # Number of cases with predictions plot 
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=cases_df['date'], y=cases_df['cases_cumsum'], line=dict(color='#7f7f7f', width=4),
                        mode='lines+markers', marker=dict(size=10), name='Dados'))
        fig_pred.add_trace(go.Scatter(x=predictions['date'], y=predictions['pred_cases'], name='Ajuste', line=dict(color='red')))

        fig_pred.update_layout(title='<b>Ajsute exponencial com previsão para os próximos 7 dias</b>',
                               yaxis_title='Casos totais')

        st.plotly_chart(fig_pred)

st.sidebar.title('Contribua')
st.sidebar.info('Este é um projeto open source e você é muito bem-vindo para **contribuir** com sugestões, ideias e desenvolvimento de novas funcionalidades. O código do projeto pode ser encontrado neste repositório do [Github](https://github.com/alexandre-martins/covid19-dashboard)')
