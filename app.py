```python
import streamlit as st
import os
import asyncio

from baixar_escala import baixar_pdf_escala
from gerar_painel import extrair_dados_pdf, gerar_escala_html


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
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
# CAMINHO PADRÃO DO PDF
# ============================================================

CAMINHO_PDF = os.path.abspath(
    os.path.join("downloads", "escala_atual.pdf")
)


# ============================================================
# BOTÃO PARA ATUALIZAR A ESCALA
# ============================================================

if st.button(
    "🔄 Atualizar escala recente",
    use_container_width=True
):

    with st.spinner(
        "Acessando o I-Flight e baixando sua escala..."
    ):

        try:

            # Executa o Playwright e recebe o caminho
            # real do arquivo baixado
            caminho_baixado = asyncio.run(
                baixar_pdf_escala()
            )

            # Verifica se o caminho retornado existe
            if (
                caminho_baixado
                and os.path.exists(caminho_baixado)
            ):

                tamanho = os.path.getsize(
                    caminho_baixado
                )

                if tamanho > 0:

                    st.success(
                        f"Escala baixada com sucesso! "
                        f"({tamanho / 1024:.1f} KB)"
                    )

                    # Guarda o caminho na sessão
                    st.session_state["pdf"] = (
                        caminho_baixado
                    )

                else:

                    st.error(
                        "O arquivo PDF foi criado, "
                        "mas está vazio."
                    )

            else:

                st.error(
                    "O download foi executado, "
                    "mas o arquivo PDF não foi encontrado "
                    "no servidor."
                )

        except Exception as e:

            st.error(
                f"Erro ao baixar a escala: {e}"
            )


# ============================================================
# DETERMINA QUAL PDF DEVE SER PROCESSADO
# ============================================================

caminho_para_processar = (
    st.session_state.get(
        "pdf",
        CAMINHO_PDF
    )
)


# ============================================================
# PROCESSAMENTO DA ESCALA
# ============================================================

if os.path.exists(caminho_para_processar):

    try:

        # --------------------------------------------------------
        # LÊ O PDF
        # --------------------------------------------------------

        eventos = extrair_dados_pdf(
            caminho_para_processar
        )


        # --------------------------------------------------------
        # VERIFICA SE ENCONTROU EVENTOS
        # --------------------------------------------------------

        if eventos:

            # ----------------------------------------------------
            # GERA O PAINEL
            # ----------------------------------------------------

            caminho_html = gerar_escala_html(
                eventos
            )


            if caminho_html:

                st.success(
                    "Escala processada com sucesso!"
                )


                # ------------------------------------------------
                # LÊ O HTML GERADO
                # ------------------------------------------------

                with open(
                    caminho_html,
                    "r",
                    encoding="utf-8"
                ) as arquivo:

                    html = arquivo.read()


                # ------------------------------------------------
                # MOSTRA O PAINEL DENTRO DO STREAMLIT
                # ------------------------------------------------

                st.components.v1.html(
                    html,
                    height=750,
                    scrolling=True
                )


            else:

                st.warning(
                    "Não foi possível gerar "
                    "o painel da escala."
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

    # ------------------------------------------------------------
    # NENHUM PDF DISPONÍVEL
    # ------------------------------------------------------------

    st.info(
        "Arquivo de escala não encontrado. "
        "Clique no botão acima para baixar."
    )
```
