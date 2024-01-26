import pandas as pd
import plotly.express as px
import streamlit as st

ib = pd.read_csv('RECLAMEAQUI_IBYTE.csv')
hp = pd.read_csv('RECLAMEAQUI_HAPVIDA.csv')
ng = pd.read_csv('RECLAMEAQUI_NAGEM.csv')

#Unindo todos os dataframes em um só
ib['EMPRESA'] = 'Ibyte'
hp['EMPRESA'] = 'Hapvida'
ng['EMPRESA'] = 'Nagem'

df = pd.concat([ib, hp, ng], ignore_index = True)

#Coluna ID
df['ID'] = df['ID'].astype(str)

#Coluna de data
df['TEMPO'] = pd.to_datetime(df['TEMPO'])

#Coluna de Estado
df['UF'] = df['LOCAL'].str.strip().str.slice(-2)
df.loc[df['UF'] == ' C', 'UF'] = 'CE'
df.loc[df['UF'] == ' P', 'UF'] = 'PE'
df.loc[df['UF'] == 'ta', 'UF'] = 'NÃO CONSTA'
df.loc[df['UF'] == '--', 'UF'] = 'NÃO CONSTA'

#Campos para os filtros
l_empresas = ['TODAS'] + list(sorted(df['EMPRESA'].unique()))
l_uf = ['TODOS'] + list(sorted(df['UF'][df['UF'] != 'NÃO CONSTA'].unique())) + ['NÃO CONSTA']
l_status = ['TODOS'] + list(sorted(df['STATUS'].unique()))
l_tamanho = max(list(len(i) for i in df['DESCRICAO'].str.strip()))
l_dt_min = min(df['TEMPO'])
l_dt_max = max(df['TEMPO'])

#Sidebar
with st.sidebar:
        f_calendario = st.date_input("SELECIONE UM PERÍODO", (l_dt_min, l_dt_max), l_dt_min, l_dt_max, format = "DD/MM/YYYY")
        f_uf = st.selectbox('SELECIONE O ESTADO', l_uf)
        f_empresa = st.radio('SELECIONE A EMPRESA', l_empresas)
        f_status = st.radio('SELECIONE O STATUS', l_status)
        f_texto = st.slider('TAMANHO DA DESCRIÇÃO', 0, l_tamanho, l_tamanho)

#Título da página
st.title('RELATÓRIO RECLAME AQUI')

st.markdown('---')

#Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Reclamações", df['EMPRESA'].count())
col2.metric("Hapvida", df.loc[df['EMPRESA'] == 'Hapvida']['EMPRESA'].count())
col3.metric("Ibyte", df.loc[df['EMPRESA'] == 'Ibyte']['EMPRESA'].count())
col4.metric("Nagem", df.loc[df['EMPRESA'] == 'Nagem']['EMPRESA'].count())

st.markdown('---')

#DF com filtros
filtro_empresa = (df['EMPRESA'] == f_empresa) if f_empresa != 'TODAS' else df['EMPRESA'].isin(l_empresas[0:])
filtro_status = (df['STATUS'] == f_status) if f_status != 'TODOS' else df['STATUS'].isin(l_status[0:])
filtro_uf = (df['UF'] == f_uf) if f_uf != 'TODOS' else df['UF'].isin(l_uf[0:])
filtro_tamanho = (df['DESCRICAO'].apply(len) <= f_texto)
filtro_data = (df['TEMPO'] >= pd.to_datetime(f_calendario[0])) & (df['TEMPO'] <= pd.to_datetime(f_calendario[1]))

df_filtrado = df[filtro_empresa & filtro_status & filtro_uf & filtro_tamanho & filtro_data]

#Gráfico frequencia de reclamações
fig_recl = px.bar(
    df_filtrado['TEMPO'].value_counts().reset_index(name = 'RECLAMAÇÕES'),
    x = 'TEMPO',
    y = 'RECLAMAÇÕES',
    title = 'FREQUÊNCIA DE RECLAMAÇÕES',
    labels = {'TEMPO':'DATA'}, 
    height = 400,
    color_continuous_scale = px.colors.sequential.Sunset
)
st.plotly_chart(fig_recl)

# Criar o gráfico de barras classificado pela quantidade de ocorrências no eixo y
fig_uf = px.bar(
    df_filtrado['UF'].value_counts().reset_index(name = 'RECLAMAÇÕES'),
    x = 'UF',
    y = 'RECLAMAÇÕES',
    title = 'RECLAMAÇÕES POR ESTADO',
    labels = {'UF':'ESTADO'}, 
    height = 400,
    color_continuous_scale = px.colors.sequential.Sunset
)
st.plotly_chart(fig_uf)

# Gráfico de Frequência por Status
fig_status = px.pie(
        df_filtrado, 
        names = 'STATUS', 
        title = 'STATUS DAS RECLAMAÇÕES')
st.plotly_chart(fig_status)

# Gráfico de Distribuição do Tamanho da Descrição
fig_tamanho = px.histogram(
        df_filtrado, 
        x = df_filtrado['DESCRICAO'].apply(len),
        nbins = 20, 
        title =' DISTRIBUIÇÃO POR TAMANHO DA DESCRIÇÃO',
        labels = {'x':'TAMANHO DA DESCRIÇÃO'}
    )
st.plotly_chart(fig_tamanho)