import streamlit as st
import requests
import pandas as pd
import random
import time



st.title("🌐 Projetos de Aula: APIs e Integrações")

tab1, = st.tabs(["CEP"])

with tab1:
    st.header("Consulta de Endereço via CEP")
    with st.container(border=True):
        cep = st.text_input("Digite o CEP (apenas números):", max_chars=8)
        if st.button("Consultar CEP"):
            if len(cep) == 8:
                try:
                    response = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
                    data = response.json()
                    if "erro" not in data:
                        st.json(data)
                    else:
                        st.error("CEP não encontrado.")
                except:
                    st.error("Erro na conexão.")
            else:
                st.warning("O CEP deve ter 8 dígitos.")


