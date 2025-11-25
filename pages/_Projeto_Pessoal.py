import streamlit as st
import json
import os
import requests
import time

if not os.path.exists('data'):
    os.makedirs('data')
    
ARQUIVO_DADOS = 'data/conversoes.json'

def carregar_historico():
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    with open(ARQUIVO_DADOS, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def salvar_historico(historico):
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(historico, f, indent=4) 

def obter_cotacoes():
    try:
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL,JPY-BRL"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter cotações da API: {e}")
        return None

def busca_recursiva(lista, termo_buscado, index=0):
    if index >= len(lista):
        return None
    
    if termo_buscado.upper() in lista[index]['moeda_origem']:
        return lista[index]
    
    return busca_recursiva(lista, termo_buscado, index + 1)

def ordenar_historico_por_valor(lista):
    n = len(lista)
    lista_ord = lista.copy()
    
    for i in range(n):
        for j in range(0, n-i-1):
            if lista_ord[j]['valor_convertido'] > lista_ord[j+1]['valor_convertido']:
                lista_ord[j], lista_ord[j+1] = lista_ord[j+1], lista_ord[j]
    return lista_ord

st.title("💰 Conversor de Moedas (API Keyless)")
cotacoes = obter_cotacoes()
historico = carregar_historico()

if cotacoes:
    st.sidebar.success("Conectado à AwesomeAPI!")
    st.subheader("Taxas Atuais (vs BRL)")
    
    moedas_disponiveis = {
        "Dólar Americano (USD)": float(cotacoes['USDBRL']['bid']),
        "Euro (EUR)": float(cotacoes['EURBRL']['bid']),
        "Bitcoin (BTC)": float(cotacoes['BTCBRL']['bid']),
        "Iene Japonês (JPY)": float(cotacoes['JPYBRL']['bid']),
    }
    
    col1, col2, col3, col4 = st.columns(4) 
    col1.metric("USD", f"R$ {float(cotacoes['USDBRL']['bid']):.4f}", f"{cotacoes['USDBRL']['pctChange']}%")
    col2.metric("EUR", f"R$ {float(cotacoes['EURBRL']['bid']):.4f}", f"{cotacoes['EURBRL']['pctChange']}%")
    col3.metric("BTC", f"R$ {float(cotacoes['BTCBRL']['bid']):.2f}")
    col4.metric("JPY", f"R$ {float(cotacoes['JPYBRL']['bid']):.4f}")
    
    st.markdown("---") 
    
    menu = st.sidebar.radio("Funções", ["Converter Moeda", "Visualizar Histórico e Big O", "Buscar no Histórico (Recursivo)"])

    
    if menu == "Converter Moeda":
        st.subheader("Nova Conversão")
        
        moeda_selecionada = st.selectbox("Moeda de Origem", list(moedas_disponiveis.keys()))
        valor_original = st.number_input("Valor a Converter (em BRL)", min_value=0.01) 
        
        submit = st.button("Realizar Conversão")
        
        if submit and valor_original:
            taxa = moedas_disponiveis[moeda_selecionada]
            valor_convertido = valor_original / taxa
            
            if valor_convertido > 0:
                st.success(f"Conversão Realizada:")
                st.markdown(f"**R$ {valor_original:.2f}** valem **{valor_convertido:.2f}** em {moeda_selecionada.split(' ')[0]}.")
                
                registro = {
                    "data": time.strftime("%d/%m/%Y %H:%M:%S"),
                    "moeda_origem": moeda_selecionada,
                    "valor_original": valor_original,
                    "valor_convertido": valor_convertido
                }
                historico.append(registro)
                salvar_historico(historico)
            else:
                st.error("Valor inválido para conversão.")

    elif menu == "Visualizar Histórico e Big O":
        st.subheader("Histórico de Conversões (Ordenado)")
        
        if historico:
            with st.expander("Clique para ver o Histórico Completo", expanded=False):
                st.info("O histórico foi ordenado usando o **Bubble Sort** ($O(n^2)$) pelo valor convertido.")
                
                historico_ordenado = ordenar_historico_por_valor(historico)
                
                with st.container(border=True): 
                    for registro in historico_ordenado:
                        st.markdown(f"**{registro['data']}** | {registro['moeda_origem']} | R$ {registro['valor_original']:.2f} -> **{registro['valor_convertido']:.2f}**")
        else:
            st.warning("Nenhuma conversão registrada ainda.")

    elif menu == "Buscar no Histórico (Recursivo)":
        st.subheader("Busca Recursiva por Moeda de Origem")
        
        with st.container(border=True):
            termo = st.text_input("Digite o código ou parte do código da moeda (Ex: USD ou EUR):")
            
            if st.button("Buscar Registro"):
                resultado = busca_recursiva(historico, termo)
                
                if resultado:
                    st.success("Registro Encontrado (Busca Recursiva):")
                    st.json(resultado)
                else:
                    st.error("Nenhum registro encontrado para essa moeda.")