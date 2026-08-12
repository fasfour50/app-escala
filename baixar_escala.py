import asyncio
import os
from playwright.async_api import async_playwright


async def baixar_pdf_escala():

    # Caminho absoluto do projeto
    pasta_downloads = os.path.abspath("downloads")
    os.makedirs(pasta_downloads, exist_ok=True)

    caminho_pdf = os.path.join(
        pasta_downloads,
        "escala_atual.pdf"
    )

    print("=" * 60)
    print("INICIANDO DOWNLOAD")
    print("=" * 60)

    print(f"Pasta de downloads: {pasta_downloads}")
    print(f"Arquivo destino: {caminho_pdf}")

    async with async_playwright() as p:

        print("1. Abrindo Chromium...")

        chromium_path = "/usr/bin/chromium"

        context = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.abspath("perfil_chrome"),
            executable_path=chromium_path,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = context.pages[0] if context.pages else await context.new_page()

        page.set_default_timeout(40000)

        print("2. Acessando I-Flight...")

        await page.goto(
            "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage",
            wait_until="domcontentloaded",
            timeout=60000
        )

        await page.wait_for_timeout(5000)

        print(f"URL atual: {page.url}")

        # ==========================================================
        # VERIFICA LOGIN
        # ==========================================================

        print("3. Procurando Roster...")

        try:

            roster_tab = page.get_by_text(
                "Roster",
                exact=True
            ).first

            await roster_tab.wait_for(
                state="visible",
                timeout=10000
            )

            print("✅ Roster encontrado.")

        except Exception as e:

            print("❌ Roster não encontrado.")
            print(f"Detalhes: {e}")

            await context.close()

            raise Exception(
                "O I-Flight não está autenticado nesta sessão."
            )

        # ==========================================================
        # ROSTER
        # ==========================================================

        print("4. Abrindo Roster...")

        await roster_tab.hover()

        await page.wait_for_timeout(1500)

        print("5. Abrindo Roster Calendar...")

        roster_calendar = page.get_by_text(
            "Roster Calendar",
            exact=False
        ).first

        await roster_calendar.click(force=True)

        await page.wait_for_timeout(4000)

        print("6. Abrindo Roster Report...")

        roster_report = page.get_by_text(
            "Roster Report",
            exact=False
        ).first

        await roster_report.click(force=True)

        await page.wait_for_timeout(5000)

        # ==========================================================
        # PDF
        # ==========================================================

        print("7. Selecionando PDF...")

        select_format = page.get_by_text(
            "Select Format",
            exact=False
        ).first

        await select_format.click(force=True)

        await page.wait_for_timeout(1000)

        try:

            pdf_item = page.get_by_text(
                "pdf",
                exact=True
            ).first

            await pdf_item.click(force=True)

        except Exception:

            await page.keyboard.type("pdf")
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(1500)

        # ==========================================================
        # DOWNLOAD
        # ==========================================================

        print("8. Executando relatório...")

        run_btn = page.get_by_text(
            "Run",
            exact=True
        ).first

        async with page.expect_download(
            timeout=60000
        ) as download_info:

            await run_btn.click(force=True)

        download = await download_info.value

        print("9. Download recebido pelo Playwright.")

        # Remove arquivo anterior
        if os.path.exists(caminho_pdf):

            try:
                os.remove(caminho_pdf)
                print("Arquivo anterior removido.")

            except Exception as e:

                print(f"⚠️ Não foi possível remover arquivo anterior: {e}")

        # Salva o arquivo
        await download.save_as(caminho_pdf)

        # ==========================================================
        # CONFIRMAÇÃO REAL
        # ==========================================================

        print("=" * 60)
        print("VERIFICANDO ARQUIVO")
        print("=" * 60)

        if os.path.exists(caminho_pdf):

            tamanho = os.path.getsize(caminho_pdf)

            print("✅ ARQUIVO EXISTE!")
            print(f"Caminho: {caminho_pdf}")
            print(f"Tamanho: {tamanho} bytes")

            if tamanho == 0:

                raise Exception(
                    "O PDF foi criado, mas está vazio."
                )

        else:

            raise Exception(
                f"Playwright informou que salvou o arquivo, "
                f"mas ele não existe em: {caminho_pdf}"
            )

        await context.close()

        print("10. Navegador fechado.")

        # Retorna o caminho para o app.py
        return caminho_pdf


if __name__ == "__main__":
    asyncio.run(baixar_pdf_escala())
