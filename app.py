import streamlit as st
import os
import asyncio
from baixar_escala import baixar_pdf_escala
from gerar_painel import extrair_dados_pdf, gerar_escala_html

# Configuração da página para ocupar bem a tela do celular
st.set_page_config(page_title="Escala I-Flight", page_icon="✈️", layout="wide")

st.title("✈️ Minha Escala I-Flight")

# Botão para baixar e atualizar a escala diretamente
if st.button("🔄 Atualizar Escala Recente", type="primary"):
    with st.spinner("Baixando a escala do I-Flight..."):
        try:
            # Executa a automação de download de forma assíncrona
            asyncio.run(baixar_pdf_escala())
            st.success("Escala baixada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao baixar a escala: {e}")

caminho_pdf = "./downloads/escala_atual.pdf"

if os.path.exists(caminho_pdf):
    st.info("📊 Processando dados e gerando painel...")
    
    # Extrai os dados do PDF utilizando a lógica correta (HSB, APZ, Voos)
    eventos = extrair_dados_pdf(caminho_pdf)
    
    if eventos:
        # Gera a página HTML estilizada
        caminho_html = gerar_escala_html(eventos)
        
        if caminho_html and os.path.exists(caminho_html):
            # Lê o conteúdo do HTML gerado para exibi-lo dentro da tela do Streamlit
            with open(caminho_html, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            st.success("Painel gerado com sucesso!")
            
            # Renderiza o painel interativo com barra de rolagem horizontal perfeita para celular
            st.components.v1.html(html_content, height=650, scrolling=True)
    else:
        st.warning("⚠️ Nenhum evento foi encontrado no PDF da escala.")
else:
    st.warning("⚠️ Arquivo de escala não encontrado. Clique no botão acima para baixar.")