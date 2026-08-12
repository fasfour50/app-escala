import asyncio
import base64
import os

import streamlit as st
from playwright.async_api import async_playwright


URL_IFLIGHT = (
    "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
)

PASTA_DOWNLOADS = os.path.abspath("downloads")

CAMINHO_PDF = os.path.join(
    PASTA_DOWNLOADS,
    "escala_atual.pdf"
)

CAMINHO_ESTADO = os.path.abspath(
    "estado_login.json"
)


def preparar_estado_login():
    """
    Cria o arquivo estado_login.json a partir do Secret
    configurado no Streamlit Cloud.
    """

    if not hasattr(st, "secrets"):
        raise Exception(
            "Os Secrets do Streamlit não estão disponíveis."
        )

    if "IFLIGHT_LOGIN_STATE" not in st.secrets:
        raise Exception(
            "Secret IFLIGHT_LOGIN_STATE não encontrado."
        )

    estado_base64 = st.secrets["IFLIGHT_LOGIN_STATE"]

    try:
        dados = base64.b64decode(estado_base64)
    except Exception as e:
        raise Exception(
            f"Não foi possível decodificar o estado de login: {e}"
        )

    with open(CAMINHO_ESTADO, "wb") as arquivo:
        arquivo.write(dados)

    tamanho = os.path.getsize(CAMINHO_ESTADO)

    if tamanho == 0:
        raise Exception(
            "O estado de login foi criado, mas está vazio."
        )

    print(
        f"Estado de login criado: {tamanho} bytes"
    )


async def baixar_pdf_escala_async():

    os.makedirs(
        PASTA_DOWNLOADS,
        exist_ok=True
    )

    preparar_estado_login()

    print("=" * 60)
    print("INICIANDO DOWNLOAD DA ESCALA")
    print("=" * 60)

    async with async_playwright() as p:

        print("Abrindo Chromium do sistema...")

        browser = await p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        context = await browser.new_context(
            storage_state=CAMINHO_ESTADO,
            accept_downloads=True,
        )

        page = await context.new_page()

        page.set_default_timeout(40000)

        print("Acessando I-Flight...")

        await page.goto(
            URL_IFLIGHT,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await page.wait_for_timeout(5000)

        print("=" * 60)
        print("DIAGNÓSTICO DA PÁGINA")
        print("=" * 60)

        print("URL atual:")
        print(page.url)

        titulo = await page.title()

        print()
        print("Título:")
        print(titulo)

        print()
        print("Verificando Roster...")

        try:

            texto = await page.locator(
                "body"
            ).inner_text(
                timeout=10000
            )

        except Exception as e:

            texto = (
                f"Não foi possível ler o texto da página: {e}"
            )

        print()
        print("Texto encontrado:")
        print(texto[:3000])

        # =====================================================
        # VERIFICAÇÃO DE AUTENTICAÇÃO
        # =====================================================

        if "Roster" not in texto:

            print()
            print("=" * 60)
            print("AUTENTICAÇÃO NÃO DETECTADA")
            print("=" * 60)

            print("URL atual:")
            print(page.url)

            print()
            print("Título:")
            print(titulo)

            print()
            print("Texto encontrado:")
            print(texto[:3000])

            try:

                await page.screenshot(
                    path="debug_autenticacao.png",
                    full_page=True
                )

                print()
                print(
                    "Screenshot salvo em: "
                    "debug_autenticacao.png"
                )

            except Exception as e:

                print(
                    f"Não foi possível criar screenshot: {e}"
                )

            await context.close()
            await browser.close()

            raise Exception(
                "O I-Flight não está autenticado. "
                f"URL atual: {page.url} | "
                f"Título: {titulo}"
            )

        print()
        print("OK: Roster encontrado.")

        # =====================================================
        # ROSTER
        # =====================================================

        print()
        print("Abrindo Roster...")

        roster_tab = page.get_by_text(
            "Roster",
            exact=True
        ).first

        await roster_tab.hover()

        await page.wait_for_timeout(1500)

        # =====================================================
        # ROSTER CALENDAR
        # =====================================================

        print("Abrindo Roster Calendar...")

        roster_calendar = page.get_by_text(
            "Roster Calendar",
            exact=False
        ).first

        await roster_calendar.click(
            force=True
        )

        await page.wait_for_timeout(4000)

        # =====================================================
        # ROSTER REPORT
        # =====================================================

        print("Abrindo Roster Report...")

        roster_report = page.get_by_text(
            "Roster Report",
            exact=False
        ).first

        await roster_report.click(
            force=True
        )

        await page.wait_for_timeout(5000)

        # =====================================================
        # SELECT FORMAT
        # =====================================================

        print("Selecionando formato...")

        select_format = page.get_by_text(
            "Select Format",
            exact=False
        ).first

        await select_format.click(
            force=True
        )

        await page.wait_for_timeout(1000)

        # =====================================================
        # PDF
        # =====================================================

        print("Selecionando PDF...")

        try:

            pdf_item = page.get_by_text(
                "pdf",
                exact=True
            ).first

            await pdf_item.click(
                force=True
            )

        except Exception:

            await page.keyboard.type("pdf")
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(1500)

        # =====================================================
        # RUN
        # =====================================================

        print("Executando relatório...")

        run_btn = page.get_by_text(
            "Run",
            exact=True
        ).first

        async with page.expect_download(
            timeout=60000
        ) as download_info:

            await run_btn.click(
                force=True
            )

        download = await download_info.value

        print("Download recebido.")

        # =====================================================
        # SALVAR PDF
        # =====================================================

        if os.path.exists(CAMINHO_PDF):

            try:

                os.remove(CAMINHO_PDF)

            except Exception:

                pass

        await download.save_as(
            CAMINHO_PDF
        )

        if not os.path.exists(CAMINHO_PDF):

            await context.close()
            await browser.close()

            raise Exception(
                "O download foi executado, "
                "mas o arquivo PDF não foi encontrado."
            )

        tamanho = os.path.getsize(
            CAMINHO_PDF
        )

        print(
            f"PDF salvo: {tamanho} bytes"
        )

        if tamanho == 0:

            await context.close()
            await browser.close()

            raise Exception(
                "O PDF foi criado, mas está vazio."
            )

        # =====================================================
        # VALIDAR PDF
        # =====================================================

        with open(
            CAMINHO_PDF,
            "rb"
        ) as arquivo:

            inicio = arquivo.read(5)

        if inicio != b"%PDF-":

            await context.close()
            await browser.close()

            raise Exception(
                "O arquivo baixado não parece ser "
                "um PDF válido."
            )

        await context.close()
        await browser.close()

        print()
        print("=" * 60)
        print("DOWNLOAD CONCLUÍDO COM SUCESSO")
        print("=" * 60)

        return CAMINHO_PDF


def baixar_pdf_escala():

    return asyncio.run(
        baixar_pdf_escala_async()
    )
