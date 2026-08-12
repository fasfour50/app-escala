import streamlit as st
import asyncio
import os

from playwright.async_api import async_playwright


URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"


async def testar_login():

    resultado = {}

    async with async_playwright() as p:

        chromium_path = "/usr/bin/chromium"

        # Usa uma pasta separada somente para este teste
        perfil = os.path.abspath("teste_perfil")

        os.makedirs(perfil, exist_ok=True)

        context = await p.chromium.launch_persistent_context(
            user_data_dir=perfil,
            executable_path=chromium_path,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = (
            context.pages[0]
            if context.pages
            else await context.new_page()
        )

        page.set_default_timeout(30000)

        try:

            st.write("1. Abrindo I-Flight...")

            await page.goto(
                URL_IFLIGHT,
                wait_until="domcontentloaded",
                timeout=60000
            )

            await page.wait_for_timeout(8000)

            resultado["url"] = page.url
            resultado["titulo"] = await page.title()

            st.write("2. Página carregada.")
            st.write("URL atual:", page.url)
            st.write("Título:", await page.title())

            # ------------------------------------------------
            # Captura o texto visível da página
            # ------------------------------------------------

            try:
                texto = await page.locator("body").inner_text(
                    timeout=10000
                )

                resultado["texto"] = texto[:5000]

            except Exception as e:

                resultado["texto"] = (
                    f"Não foi possível ler o texto: {e}"
                )

            # ------------------------------------------------
            # Verifica elementos relacionados ao Google
            # ------------------------------------------------

            google_textos = [
                "Sign in with Google",
                "Google",
                "accounts.google.com",
                "Choose an account",
                "Sign in"
            ]

            encontrados = []

            for item in google_textos:

                try:

                    if item.lower() in (
                        resultado["texto"].lower()
                    ):
                        encontrados.append(item)

                except Exception:
                    pass

            resultado["google"] = encontrados

            # ------------------------------------------------
            # Verifica Roster
            # ------------------------------------------------

            try:

                roster = page.get_by_text(
                    "Roster",
                    exact=True
                ).first

                if await roster.is_visible(
                    timeout=5000
                ):
                    resultado["roster"] = True

                else:
                    resultado["roster"] = False

            except Exception:

                resultado["roster"] = False

            # ------------------------------------------------
            # Screenshot para diagnóstico
            # ------------------------------------------------

            screenshot = "teste_login.png"

            await page.screenshot(
                path=screenshot,
                full_page=True
            )

            resultado["screenshot"] = screenshot

        except Exception as e:

            resultado["erro"] = str(e)

        finally:

            await context.close()

    return resultado


# ============================================================
# INTERFACE STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Teste Login I-Flight",
    page_icon="✈️"
)

st.title("✈️ Teste de Login I-Flight")

st.write(
    "Este teste verifica se o servidor consegue acessar "
    "o I-Flight e identificar a tela de autenticação."
)

if st.button(
    "🔐 Testar acesso ao I-Flight",
    use_container_width=True
):

    with st.spinner(
        "Acessando o I-Flight..."
    ):

        try:

            resultado = asyncio.run(
                testar_login()
            )

            st.success(
                "Teste concluído."
            )

            st.subheader("Resultado")

            st.write(
                "URL:",
                resultado.get("url", "não disponível")
            )

            st.write(
                "Título:",
                resultado.get("titulo", "não disponível")
            )

            if resultado.get("roster"):

                st.success(
                    "✅ Roster encontrado. "
                    "A sessão já está autenticada."
                )

            else:

                st.warning(
                    "⚠️ Roster não encontrado."
                )

            if resultado.get("google"):

                st.info(
                    "Elementos relacionados ao Google encontrados:"
                )

                st.write(
                    resultado["google"]
                )

            st.subheader(
                "Texto encontrado na página"
            )

            st.code(
                resultado.get(
                    "texto",
                    "Nenhum texto encontrado."
                )
            )

            if resultado.get("erro"):

                st.error(
                    "Erro durante o teste:"
                )

                st.code(
                    resultado["erro"]
                )

        except Exception as e:

            st.error(
                f"Erro ao executar teste: {e}"
            )
