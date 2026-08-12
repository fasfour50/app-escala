import streamlit as st
import os
import subprocess
import sys

from baixar_escala import baixar_pdf_escala


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Minha Escala",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF = os.path.join(
    BASE_DIR,
    "downloads",
    "escala_atual.pdf"
)

HTML = os.path.join(
    BASE_DIR,
    "minha_escala.html"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("✈️ Minha Escala")


# ============================================================
# ATUALIZAR ESCALA
# ============================================================

if st.button(
    "🔄 Atualizar escala",
    type="primary",
    use_container_width=True
):

    try:

        with st.spinner(
            "Acessando o I-Flight e baixando a escala..."
        ):

            pdf = baixar_pdf_escala()

        st.success(
            "Escala baixada com sucesso."
        )

        # ----------------------------------------------------
        # GERAR PAINEL
        # ----------------------------------------------------

        with st.spinner(
            "Gerando painel..."
        ):

            resultado = subprocess.run(
                [
                    sys.executable,
                    os.path.join(
                        BASE_DIR,
                        "gerar_painel.py"
                    )
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

        if resultado.returncode != 0:

            st.error(
                "Erro ao gerar o painel."
            )

            if resultado.stdout:
                st.code(resultado.stdout)

            if resultado.stderr:
                st.code(resultado.stderr)

        else:

            st.success(
                "Escala atualizada."
            )

            st.rerun()

    except Exception as e:

        st.error(
            "Não foi possível atualizar a escala."
        )

        st.exception(e)


# ============================================================
# MOSTRAR PAINEL
# ============================================================

if os.path.exists(HTML):

    with open(
        HTML,
        "r",
        encoding="utf-8"
    ) as arquivo:

        html = arquivo.read()

    st.components.v1.html(
        html,
        height=1000,
        scrolling=True
    )

else:

    st.info(
        "A escala ainda não foi carregada. "
        "Clique em 'Atualizar escala'."
    )
