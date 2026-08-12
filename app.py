import streamlit as st
import streamlit.components.v1 as components
import subprocess
import os
import sys

st.set_page_config(
    page_title="Minha Escala",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PASTA = r"C:\iflight"
HTML = os.path.join(PASTA, "minha_escala.html")
ATUALIZADOR = os.path.join(PASTA, "atualizar_escala.py")

st.title("Minha Escala")

if st.button("Atualizar escala", type="primary"):
    with st.spinner("Atualizando escala..."):
        resultado = subprocess.run(
            [sys.executable, ATUALIZADOR],
            cwd=PASTA,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

    if resultado.returncode == 0:
        st.success("Escala atualizada com sucesso.")
        st.rerun()
    else:
        st.error("Erro ao atualizar a escala.")
        if resultado.stdout:
            st.text("Saída:")
            st.code(resultado.stdout)
        if resultado.stderr:
            st.text("Erro:")
            st.code(resultado.stderr)

if os.path.exists(HTML):
    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()

    components.html(html, height=900, scrolling=True)
else:
    st.error("Arquivo minha_escala.html não encontrado.")
