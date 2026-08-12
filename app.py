import os
import streamlit as st
import streamlit.components.v1 as components

from baixar_escala import baixar_pdf_escala


st.set_page_config(
    page_title="Minha Escala",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML = os.path.join(
    BASE_DIR,
    "minha_escala.html"
)

st.title("Minha Escala")

if st.button(
    "Atualizar escala",
    type="primary"
):

    with st.spinner(
        "Atualizando escala..."
    ):

        try:

            pdf = baixar_pdf_escala()

            st.success(
                "Escala atualizada com sucesso."
            )

            st.rerun()

        except Exception as e:

            st.error(
                "Não foi possível atualizar a escala."
            )

            st.exception(e)

if os.path.exists(HTML):

    with open(
        HTML,
        "r",
        encoding="utf-8"
    ) as arquivo:

        html = arquivo.read()

    components.html(
        html,
        height=1200,
        scrolling=True
    )

else:

    st.error(
        "Arquivo minha_escala.html não encontrado."
    )
