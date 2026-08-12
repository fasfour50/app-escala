import streamlit as st
import os
import asyncio

from baixar_escala import baixar_pdf_escala
from gerar_painel import extrair_dados_pdf, gerar_escala_html


# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Minha Escala I-Flight",
    page_icon="✈️",
    layout="wide"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("✈️ Minha Escala I-Flight")


# ============================================================
# CAMINHO DO PDF
# ============================================================

CAMINHO_PDF = "./downloads/escala_atual.pdf"


# ============================================================
# BOTÃO PARA ATUALIZAR
# ============================================================

if st.button(
    "🔄 Atualizar escala recente",
    use_container_width=True
):

    with st.spinner("Acessando o I-Flight e baixando sua escala..."):

        try:
            asyncio.run(baixar_pdf_escala())

            # Verifica se o arquivo realmente existe
            if os.path.exists(CAMINHO_PDF):

                tamanho = os.path.getsize(CAMINHO_PDF)

                if tamanho > 0:

                    st.success(
                        f"Escala baixada com sucesso! "
                        f"({tamanho / 1024:.1f} KB)"
                    )

                    # Guarda o caminho na sessão
                    st.session_state["pdf"] = CAMINHO_PDF

                else:
                    st.error(
                        "O arquivo foi criado, mas está vazio."
                    )

            else:

                st.error(
                    "O download foi executado, mas o arquivo PDF "
                    "não foi encontrado no servidor."
                )

        except Exception as e:

            st.error(
                f"Erro ao baixar a escala: {e}"
            )


# ============================================================
# VERIFICA SE EXISTE PDF
# ============================================================

if os.path.exists(CAMINHO_PDF):

    try:

        # ========================================================
        # EXTRAI OS DADOS
        # ========================================================

        eventos = extrair_dados_pdf(CAMINHO_PDF)

        if eventos:

            # ====================================================
            # GERA O PAINEL
            # ====================================================

            caminho_html = gerar_escala_html(eventos)

            if caminho_html:

                st.success("Escala processada com sucesso!")

                # Lê o HTML gerado
                with open(
                    caminho_html,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    html = arquivo.read()

                # Mostra o painel diretamente dentro do Streamlit
                st.components.v1.html(
                    html,
                    height=700,
                    scrolling=True
                )

            else:

                st.warning(
                    "Não foi possível gerar o painel da escala."
                )

        else:

            st.warning(
                "O PDF foi baixado, mas nenhum evento "
                "foi encontrado na escala."
            )

else:

    st.info(
        "Arquivo de escala não encontrado. "
        "Clique no botão acima para baixar."
    )
