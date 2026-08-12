import streamlit as st
import os
import asyncio

from baixar_escala import baixar_pdf_escala
from gerar_painel import extrair_dados_pdf, gerar_escala_html


st.set_page_config(
    page_title="Minha Escala I-Flight",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Minha Escala I-Flight")

CAMINHO_PDF = "./downloads/escala_atual.pdf"


if st.button(
    "🔄 Atualizar escala recente",
    use_container_width=True
):

    with st.spinner("Acessando o I-Flight e baixando sua escala..."):

        try:
            asyncio.run(baixar_pdf_escala())

            if os.path.exists(CAMINHO_PDF):

                tamanho = os.path.getsize(CAMINHO_PDF)

                if tamanho > 0:
                    st.success(
                        f"Escala baixada com sucesso! "
                        f"({tamanho / 1024:.1f} KB)"
                    )
                else:
                    st.error("O arquivo PDF foi criado, mas está vazio.")

            else:
                st.error(
                    "O download foi executado, mas o arquivo PDF "
                    "não foi encontrado no servidor."
                )

        except Exception as e:
            st.error(f"Erro ao baixar a escala: {e}")


# ============================================================
# PROCESSAMENTO DO PDF
# ============================================================

if os.path.exists(CAMINHO_PDF):

    try:

        eventos = extrair_dados_pdf(CAMINHO_PDF)

        if eventos:

            caminho_html = gerar_escala_html(eventos)

            if caminho_html:

                st.success("Escala processada com sucesso!")

                with open(
                    caminho_html,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    html = arquivo.read()

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

    except Exception as e:

        st.error(
            f"Erro ao processar a escala: {e}"
        )

else:

    st.info(
        "Arquivo de escala não encontrado. "
        "Clique no botão acima para baixar."
    )
