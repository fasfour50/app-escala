import asyncio
import os
from playwright.async_api import async_playwright

URL = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
ESTADO = r"C:\iflight\estado_login.json"
PASTA = r"C:\iflight\downloads"

async def teste():
    os.makedirs(PASTA, exist_ok=True)

    async with async_playwright() as p:
        print("Abrindo Chromium...")

        browser = await p.chromium.launch(headless=true)

        context = await browser.new_context(
            storage_state=ESTADO,
            accept_downloads=True
        )

        page = await context.new_page()
        page.set_default_timeout(30000)

        print("Acessando I-Flight...")

        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        await page.wait_for_timeout(5000)

        print("URL:", page.url)

        texto = await page.locator("body").inner_text()

        if "Roster" not in texto:
            print("ERRO: Roster não encontrado.")
            print(texto[:3000])
            await browser.close()
            return

        print("OK: Roster encontrado.")

        print("Abrindo Roster...")

        roster = page.get_by_text("Roster", exact=True).first
        await roster.click(force=True)

        await page.wait_for_timeout(1500)

        print("Abrindo Roster Calendar...")

        calendar = page.get_by_text(
            "Roster Calendar",
            exact=False
        ).first

        await calendar.click(force=True)

        await page.wait_for_timeout(4000)

        print("Abrindo Roster Report...")

        report = page.get_by_text(
            "Roster Report",
            exact=False
        ).first

        await report.click(force=True)

        await page.wait_for_timeout(5000)

        print("Selecionando formato...")

        formato = page.get_by_text(
            "Select Format",
            exact=False
        ).first

        await formato.click(force=True)

        await page.wait_for_timeout(1000)

        print("Selecionando PDF...")

        pdf = page.get_by_text(
            "pdf",
            exact=True
        ).first

        await pdf.click(force=True)

        await page.wait_for_timeout(1000)

        print("Executando relatório...")

        run = page.get_by_text(
            "Run",
            exact=True
        ).first

        async with page.expect_download(timeout=60000) as info:
            await run.click(force=True)

        download = await info.value

        arquivo = os.path.join(
            PASTA,
            "escala_atual.pdf"
        )

        await download.save_as(arquivo)

        print("")
        print("========================================")
        print("DOWNLOAD CONCLUÍDO")
        print("========================================")

        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)

            print("Arquivo:", arquivo)
            print("Tamanho:", tamanho, "bytes")

            if tamanho > 0:
                print("SUCESSO: PDF baixado corretamente.")
            else:
                print("ERRO: PDF vazio.")
        else:
            print("ERRO: PDF não encontrado.")

        input("Pressione ENTER para fechar o navegador...")

        await browser.close()

asyncio.run(teste())
