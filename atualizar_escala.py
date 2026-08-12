import asyncio
import os
import subprocess
from playwright.async_api import async_playwright

URL = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
ESTADO = r"C:\iflight\estado\_login.json"
DOWNLOAD_DIR = r"C:\iflight\downloads"
PDF_FINAL = os.path.join(DOWNLOAD_DIR, "escala_atual.pdf")


async def teste():

    print("Abrindo Chromium...")

    if not os.path.exists(ESTADO):
        print("ERRO: estado de login não encontrado:")
        print(ESTADO)
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=False)

        context = await browser.new_context(
            storage_state=ESTADO,
            accept_downloads=True
        )

        page = await context.new_page()

        print("Acessando I-Flight...")

        await page.goto(
            URL,
            wait_until="networkidle",
            timeout=120000
        )

        await page.wait_for_timeout(2000)

        # =========================================================
        # ROSTER
        # =========================================================

        print("=== PROCURANDO ROSTER ===")

        # IMPORTANTE:
        # Roster e Roster Calendar são elementos diferentes.
        # O Calendar fica escondido até passar o mouse sobre Roster.

        roster = page.locator(
            'a[ng-click="loadRosterCalendar()"]'
        ).first

        # O texto "Roster" pode estar no elemento visível
        # mesmo quando o Calendar está escondido.
        roster_visible = page.locator("a").filter(
            has_text="Roster"
        ).filter(
            has_not_text="Calendar"
        ).first

        if await roster_visible.count() == 0:
            print("ERRO: Roster não encontrado.")
            await page.screenshot(
                path=r"C:\iflight\debug_roster_erro.png"
            )
            await browser.close()
            return

        print("Roster encontrado.")

        # =========================================================
        # POSICIONAR MOUSE SOBRE ROSTER
        # =========================================================

        print("Posicionando mouse sobre Roster...")

        await roster_visible.hover()

        await page.wait_for_timeout(1500)

        print("Mouse posicionado sobre Roster.")

        # =========================================================
        # ROSTER CALENDAR
        # =========================================================

        print("Procurando Roster Calendar...")

        roster_calendar = page.locator(
            'a[ng-click="loadRosterCalendar()"]'
        ).first

        try:
            await roster_calendar.wait_for(
                state="visible",
                timeout=10000
            )
        except Exception:
            print("ERRO: Roster Calendar não ficou visível.")
            await page.screenshot(
                path=r"C:\iflight\debug_calendar_erro.png"
            )
            await browser.close()
            return

        print("Roster Calendar encontrado.")

        await roster_calendar.click()

        await page.wait_for_timeout(2000)

        print("Roster Calendar aberto.")

        # =========================================================
        # ROSTER REPORT
        # =========================================================

        print("Procurando Roster Report...")

        roster_report = page.locator(
            'button[ng-click="loadRosterReport()"]'
        ).first

        try:
            await roster_report.wait_for(
                state="visible",
                timeout=30000
            )
        except Exception:
            print("ERRO: Roster Report não encontrado.")

            await page.screenshot(
                path=r"C:\iflight\debug_roster_report_erro.png"
            )

            await browser.close()
            return

        print("Roster Report encontrado.")

        await roster_report.click()

        await page.wait_for_timeout(2500)

        print("Roster Report aberto.")

        # =========================================================
        # SELECT FORMAT
        # =========================================================

        print()
        print("=== SELECT FORMAT ===")

        # O Select Format é um botão/dropdown.
        select_format = page.get_by_text(
            "Select Format",
            exact=True
        ).last

        try:
            await select_format.wait_for(
                state="visible",
                timeout=30000
            )
        except Exception:
            print("ERRO: Select Format não encontrado.")

            await page.screenshot(
                path=r"C:\iflight\debug_select_format_erro.png"
            )

            await browser.close()
            return

        print("Select Format encontrado.")

        await select_format.click()

        await page.wait_for_timeout(700)

        # =========================================================
        # PDF
        # =========================================================

        print()
        print("=== PROCURANDO PDF ===")

        pdf = page.get_by_text(
            "pdf",
            exact=True
        ).last

        try:
            await pdf.wait_for(
                state="visible",
                timeout=10000
            )
        except Exception:
            print("ERRO: opção PDF não encontrada.")

            await page.screenshot(
                path=r"C:\iflight\debug_pdf_erro.png"
            )

            await browser.close()
            return

        print("PDF encontrado.")

        await pdf.click()

        await page.wait_for_timeout(500)

        print("PDF selecionado.")

        # =========================================================
        # RUN
        # =========================================================

        print()
        print("=== PROCURANDO RUN ===")

        run_button = page.locator(
            "button"
        ).filter(
            has_text="Run"
        ).first

        try:
            await run_button.wait_for(
                state="visible",
                timeout=30000
            )
        except Exception:
            print("ERRO: botão Run não encontrado.")

            await page.screenshot(
                path=r"C:\iflight\debug_run_erro.png"
            )

            await browser.close()
            return

        print("Botão Run encontrado.")

        # Remove o PDF anterior.
        if os.path.exists(PDF_FINAL):
            os.remove(PDF_FINAL)

        print("Clicando em Run e aguardando download...")

        try:
            async with page.expect_download(
                timeout=120000
            ) as download_info:

                await run_button.click()

            download = await download_info.value

        except Exception as erro:
            print("ERRO durante o download:")
            print(erro)

            await page.screenshot(
                path=r"C:\iflight\debug_download_erro.png"
            )

            await browser.close()
            return

        print()
        print("======================================")
        print("DOWNLOAD DETECTADO!")
        print("======================================")

        print("Nome original:")
        print(download.suggested_filename)

        await download.save_as(PDF_FINAL)

        print("Arquivo salvo em:")
        print(PDF_FINAL)

        print(
            "Tamanho:",
            os.path.getsize(PDF_FINAL),
            "bytes"
        )

        await browser.close()

    # =============================================================
    # GERAR PAINEL
    # =============================================================

    print()
    print("======================================")
    print("GERANDO PAINEL")
    print("======================================")

    resultado = subprocess.run(
        ["python", r"C:\iflight\gerar_painel.py"],
        cwd=r"C:\iflight",
        capture_output=True,
        text=True
    )

    if resultado.stdout:
        print(resultado.stdout)

    if resultado.stderr:
        print("ERROS:")
        print(resultado.stderr)

    print("======================================")
    print("PROCESSO FINALIZADO")
    print("======================================")


if __name__ == "__main__":
    asyncio.run(teste())

