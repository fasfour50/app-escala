import asyncio
import os
from playwright.async_api import async_playwright

URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
ARQUIVO_ESTADO = "estado/_login.json"
PASTA_DEBUG = "debug"
PASTA_DOWNLOADS = "downloads/escala"


async def salvar_debug(page, nome):
    os.makedirs(PASTA_DEBUG, exist_ok=True)

    await page.screenshot(
        path=f"{PASTA_DEBUG}/{nome}.png",
        full_page=True
    )

    with open(
        f"{PASTA_DEBUG}/{nome}.html",
        "w",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(await page.content())

    print(f"DEBUG salvo: {nome}")


async def teste():

    print("Abrindo Chromium...")

    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        context = await browser.new_context(
            storage_state=ARQUIVO_ESTADO,
            accept_downloads=True
        )

        page = await context.new_page()

        page.set_default_timeout(30000)

        print("Acessando I-Flight...")

        await page.goto(
            URL_IFLIGHT,
            wait_until="domcontentloaded",
            timeout=60000
        )

        await page.wait_for_timeout(5000)

        await salvar_debug(page, "debug_01_inicio")

        print("URL atual:")
        print(page.url)

        texto = await page.locator("body").inner_text()

        print("Verificando Roster...")

        if "Roster" not in texto:
            print("ERRO: Roster não encontrado.")
            print(texto[:5000])

            await salvar_debug(page, "debug_ERRO_roster")

            await browser.close()
            return

        print("OK: Roster encontrado.")

        print("Abrindo Roster...")

        roster = page.get_by_text("Roster", exact=True)

        print("Quantidade de elementos Roster:", await roster.count())

        if await roster.count() == 0:
            print("ERRO: Roster não encontrado como elemento.")

            await salvar_debug(page, "debug_ERRO_roster_elemento")

            await browser.close()
            return

        await roster.first.click()

        await page.wait_for_timeout(3000)

        await salvar_debug(page, "debug_02_roster")

        print("Abrindo Roster Calendar...")

        calendar = page.get_by_text(
            "Roster Calendar",
            exact=True
        )

        print(
            "Quantidade de elementos Roster Calendar:",
            await calendar.count()
        )

        if await calendar.count() == 0:

            print("ERRO: Roster Calendar não encontrado.")

            print(
                await page.locator("body").inner_text()
            )

            await salvar_debug(
                page,
                "debug_ERRO_calendar"
            )

            await browser.close()
            return

        await calendar.first.click()

        await page.wait_for_timeout(3000)

        await salvar_debug(page, "debug_03_calendar")

        print("Abrindo Roster Report...")

        report = page.get_by_text(
            "Roster Report",
            exact=True
        )

        print(
            "Quantidade de elementos Roster Report:",
            await report.count()
        )

        if await report.count() == 0:

            print("ERRO: Roster Report não encontrado.")

            print(
                await page.locator("body").inner_text()
            )

            await salvar_debug(
                page,
                "debug_ERRO_report"
            )

            await browser.close()
            return

        await report.first.click()

        await page.wait_for_timeout(3000)

        await salvar_debug(page, "debug_04_report")

        print("Tela do relatório carregada.")

        print("Texto da página:")

        texto = await page.locator("body").inner_text()

        print(texto[:10000])

        print()
        print("Procurando opções de PDF...")

        pdf = page.get_by_text(
            "PDF",
            exact=True
        )

        print(
            "Quantidade de elementos PDF:",
            await pdf.count()
        )

        await salvar_debug(
            page,
            "debug_05_antes_pdf"
        )

        if await pdf.count() > 0:

            await pdf.first.click()

            print("PDF selecionado.")

            await page.wait_for_timeout(2000)

            await salvar_debug(
                page,
                "debug_06_pdf_selecionado"
            )

        else:

            print("PDF não encontrado.")

        print()
        print("Procurando botões de execução...")

        botoes = page.locator("button")

        quantidade = await botoes.count()

        print("Quantidade de botões:", quantidade)

        for i in range(quantidade):

            try:

                texto_botao = (
                    await botoes.nth(i).inner_text()
                ).strip()

                print(
                    f"BOTÃO {i}: [{texto_botao}]"
                )

            except Exception:
                pass

        await salvar_debug(
            page,
            "debug_07_botoes"
        )

        print()
        print("Fim do teste de diagnóstico.")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(teste())
