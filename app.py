import streamlit as st
import numpy as np 
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
from scrapping import DataFetcher
from seir import SeirModel

corona = Image.open('images/title_logo.PNG')

st.image(corona) 

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
    model = st.sidebar.radio('', ['Exponencial e Polinomial', 'Rede Neural Artificial', 'SEIR (Simulação)'])

    if model == 'Exponencial e Polinomial':
        st.markdown('## Modelo Exponencial')
        st.write('O modelo exponencial é indicado para modelar a epidemia nos seus estágios iniciais.')
        st.write('Contudo, a análise da adequação da curva de casos ao modelo exponencial nos informa a respeito das medidas de contenção que estão sendo adotadas.')
        st.write('Caso o ajuste ao modelo não seja satisfatório, significa que as medidas de contenção estão surtindo efeito em freiar a epidemia que, caso as medidas de contenção fossem inexistentes, teria seu número casos acompanhando a curva exponencial.')

        cases_last_21days, predictions, r2 = webscrapping.get_predictions()
        cases_df = webscrapping.cases_per_day

        # Quality of last 10 days fitting to exponential model plot
        fig_quality = go.Figure()
        fig_quality.add_trace(go.Scatter(x=cases_last_21days['date'], y=cases_last_21days['log_cumsum'], line=dict(color='firebrick', width=4),
                        mode='lines+markers', marker=dict(size=10), name='Real'))
        fig_quality.add_trace(go.Scatter(x=cases_last_21days['date'], y=np.log(predictions['pred_cases']), name='Ajustado'))

        fig_quality.add_annotation(x=cases_last_21days['date'][17], y=cases_last_21days['log_cumsum'][5], text='R² = {}'.format(r2))

        fig_quality.update_annotations(dict(xref="x", yref="y", showarrow=False))

        fig_quality.update_layout(title='<b>Qualidade do ajuste exponencial em janela de 20 dias</b>',
                                  yaxis_title='log (casos totais)')

        st.plotly_chart(fig_quality, use_container_width=True)

        # Number of cases with predictions plot 
        fig_pred = go.Figure()
        fig_pred.add_trace(go.Scatter(x=cases_df['date'], y=cases_df['cases_cumsum'], line=dict(color='#7f7f7f', width=4),
                        mode='lines+markers', marker=dict(size=10), name='Dados'))
        fig_pred.add_trace(go.Scatter(x=predictions['date'], y=predictions['pred_cases'], name='Ajuste', line=dict(color='red')))

        fig_pred.update_layout(title='<b>Ajsute exponencial com previsão para os próximos 7 dias</b>',
                               yaxis_title='Casos totais')

        st.plotly_chart(fig_pred, use_container_width=True)

        st.markdown('## Modelo Polinomial')

        st.write('Em desenvolvimento...')
    
    if model == 'Rede Neural Artificial':
        st.markdown('## Rede Neural Artificial')
        st.write('Em desenvolvimento...')

    if model == 'SEIR (Simulação)':
        st.markdown('## Modelo SEIR')
        st.write(
        '''
        SEIR é um modelo comportamental em epidemiologia que busca modelar como uma doença se espalha através de uma população.
        SEIR é um acrônimo para **S**usceptible, **E**xposed, **I**nfected, **R**ecovered, ou em português: Suscetíveis, Expostos, Infectados e Recuperados.
        A ideia básica é que, quando uma doença é introduzida em uma população, as pessoas se movem de um estágio do modelo para o outro. Ou seja, as pessoas suscetíveis podem se expor ao vírus, contraí-lo e eventualmente se recuperar ou padecer.
        ''')
        
        seir_image = Image.open('images/seir.PNG')
        st.image(seir_image, use_column_width=True)

        st.write(
        '''
        A modelagem leva em consideração três parâmetros principais: $\\alpha$, $\\beta$ e $\\gamma$.
        * $\\alpha$ é o inverso do período de incubação do vírus. Tempo de incubação é o período em que o vírus fica no corpo da pessoa sem produzir sintomas.
        * $\\beta$ é a taxa de contato médio na população. Este é o parâmetro influenciado por medidas de contenção social.
        * $\\gamma$ é o inverso da média do período de infecção. Período de infecção é o tempo em que uma pessoa fica acometida pelo vírus e pode transmití-lo.

        Para essa modelagem, o valor de cada parâmetro foi retirado de artigos publicados na área, especificamente:
        * [Epidemic analysis of COVID-19 in China by dynamical modeling](https://arxiv.org/pdf/2002.06563.pdf)
        * [Impact of non-pharmaceutical interventions (NPIs) to reduce COVID19 mortality and healthcare demand](https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-NPI-modelling-16-03-2020.pdf)
        ''') 

        st.markdown('### Como a modelagem foi feita para o Brasil')
        st.write(
        '''
        Para o caso do Brasil, foi considerada uma população de 200 milhões de pessoas, sendo o número inicial de infectados
        o número total de casos mais recentes que temos. Foi considerado que toda a população é suscetível e que, inicialmente,
        o número de pessoas expostas (que contraíram o vírus mas estão em período de incubação) é 15 vezes o número de casos confirmados.
        O fator 15 foi retirado de uma estimativa realizada em declarações do Ministério da Saúde.

        A simulação sempre parte do cenário mais atual, ou seja, do dia de hoje considerando os números mais atualizados que temos.

        O objetivo é tentar prever o cenário futuro baseado nos números mais recentes que temos e também demonstrar, neste cenário,
        o impacto das medidas de isolamento social. Na simulação, o fator de contenção social foi levado em conta por meio do parâmetro *p*, 
        que possui valores entre 0 e 1. O valor de *p* = 1 seria o caso em que nenhuma medida de contenção social é adotada, ou seja, a vida cotinua normalmente.
        O valor de *p* = 0 é apenas teórico, pois significaria zerar a taxa de transmissão do vírus, ou seja, absolutamente nenhuma transmissão entre a população.

        A seguir é possível verificar os resultados da simulação para o cenário brasileiro, partindo de hoje e considerando os números mais recentes. 
        ''')
        seir_model = SeirModel(100, int(webscrapping.total_cases.replace('.', '')), 1)
        S, E, I, R = seir_model.get_model_results()
        population = seir_model.N
        
        # Prepare dates for plotting
        start = pd.Timestamp('now')
        end=pd.Timestamp('now') + pd.Timedelta(seir_model.t_max, unit='D')
        timestamp_range = np.linspace(start.value, end.value, len(seir_model.t))
        timestamp_range = pd.to_datetime(timestamp_range)

        st.markdown('#### Projeções do modelo SEIR para o Brasil (cenário sem medidas de contenção)')
        # Plotting with matplotlib
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, axisbelow=True)
        ax.plot(timestamp_range, I*population/1000000, 'r', alpha=0.8, lw=2, label='Infectados')
        ax.plot(timestamp_range, E*population/1000000, 'b', alpha=0.8, lw=2, label='Expostos')
        ax.plot(timestamp_range, R*population/1000000, 'g', alpha=0.5, lw=2, label='Recuperados com imunidade')
        ax.plot(timestamp_range, S*population/1000000, 'm', alpha=0.5, lw=2, label='Suscetíveis')
        ax.set_ylabel('População (em milhões)')
        ax.yaxis.set_tick_params(length=0)
        ax.xaxis.set_tick_params(length=0)
        ax.format_xdata = mdates.DateFormatter('%d-%m-%Y')
        plt.xticks(rotation=45)
        ax.grid(b=True, which='major', axis='both')
        legend = ax.legend(loc='best')
        legend.get_frame().set_alpha(0.8)
        plt.tight_layout()
        for spine in ('top', 'right', 'bottom', 'left'):
            ax.spines[spine].set_visible(False)

        st.pyplot()

        st.write(
        '''
        A seguir, o efeito do isolamento social é considerado na simulação. Através do parâmetro **p**, em que seu valor máximo
        representa completa ausência de isolamento social e seu valor mínimo representa taxa de transmissão nula, é possível verificar os diferentes
        cenários da epidemia no Brasil.

        Foi considerando que 20% dos infectados totais apresentarão agravamento em seu quadro clínico, ocupando leitos de hospitais.
        No Brasil, atualmente temos **270.880 leitos gerais** ao todo, segundo informações do [Cedeplar](https://www.cedeplar.ufmg.br/noticias/1223-nota-tecnica-analise-de-demanda-e-oferta-de-leitos-hospitalares-gerais-uti-e-equipamentos-de-ventilacao-assistida-no-brasil-em-funcao-da-pandemia-do-covid-19).
        Contudo, vale lembrar que uma porcentagem considerável dos leitos já são ocupados normalmente em decorrência de outras enfermidades. Portanto, 
        este número de leitos **não** está disponível apenas para o acolhimento de doentes infectados pelo coronavírus. O número real é ainda menor.

        Arraste o seletor para determinar o valor do parâmetro p e avaliar o impacto do coronavírus no sistema de saúde, considerando os dados mais atuais na simulação.
        ''')

        p = st.slider(label='Selecione o valor de p', min_value=0.5, max_value=1.0, value=1.0, step=0.01)
        seir_model_varying = SeirModel(250, int(webscrapping.total_cases.replace('.', '')), p)
        S, E, I, R = seir_model_varying.get_model_results()

        # Prepare dates for plotting
        start_var = pd.Timestamp('now')
        end_var = pd.Timestamp('now') + pd.Timedelta(seir_model_varying.t_max, unit='D')
        timestamp_range = np.linspace(start_var.value, end_var.value, len(seir_model_varying.t))
        timestamp_range = pd.to_datetime(timestamp_range)

        # Plotly plot
        fig_model = go.Figure()

        fig_model.add_trace(go.Scatter(x=timestamp_range, y=I*population/1000000, name='Infectados', line = dict(color='red')))
        fig_model.add_trace(go.Scatter(x=timestamp_range, y=I*0.2*population/1000000, name='Atendimento hospitalar', line = dict(color='royalblue'), fill='tozeroy'))
        fig_model.add_trace(go.Scatter(x=[timestamp_range[2100]], y=[0.8], text=['Leitos disponíveis'], mode='text', showlegend=False))
        fig_model.add_shape(type='line', x0=min(timestamp_range), y0=0.270880, x1=max(timestamp_range), y1=0.270880, line=dict(color='gray', dash='dash'))

        fig_model.update_layout(title={'text': '<b>Cenário da epidemia com p = {}</b>'.format(p), 'x': 0.5, 'xanchor': 'center'},
                        yaxis_title='População (em milhões)', legend_orientation="h")

        fig_model['layout']['yaxis1'].update(range=[0, 15], dtick=5, autorange=False)

        st.plotly_chart(fig_model, use_container_width=True)

st.sidebar.title('Contribua')
st.sidebar.info('Este é um projeto open source **em desenvolvimento** e você é muito bem-vindo para **contribuir** com sugestões, ideias e desenvolvimento de novas funcionalidades. O código do projeto pode ser encontrado neste repositório do [Github](https://github.com/alexandre-martins/covid19-dashboard)')
