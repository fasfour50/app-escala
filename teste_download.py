import asyncio
import os
from playwright.async_api import async_playwright

URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
ARQUIVO_ESTADO = "estado/_login.json"
PASTA_DOWNLOADS = "downloads/escala"


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

        print("URL:", page.url)

        texto = await page.locator("body").inner_text()

        if "Roster" not in texto:
            print("ERRO: Roster não encontrado.")
            print(texto[:5000])
            await browser.close()
            return

        print("OK: Roster encontrado.")

        print("Abrindo Roster...")

        roster = page.get_by_text("Roster", exact=True)

        if await roster.count() == 0:
            print("ERRO: botão Roster não encontrado.")
            await browser.close()
            return

        await roster.first.click()

        await page.wait_for_timeout(3000)

        print("Abrindo Roster Calendar...")

        calendar = page.get_by_text("Roster Calendar", exact=True)

        if await calendar.count() == 0:
            print("ERRO: Roster Calendar não encontrado.")
            await browser.close()
            return

        await calendar.first.click()

        await page.wait_for_timeout(3000)

        print("Abrindo Roster Report...")

        report = page.get_by_text("Roster Report", exact=True)

        if await report.count() == 0:
            print("ERRO: Roster Report não encontrado.")
            await browser.close()
            return

        await report.first.click()

        await page.wait_for_timeout(3000)

        print("Selecionando formato...")

        # Procura controles relacionados a formato
        texto = await page.locator("body").inner_text()
        print(texto[:3000])

        print("Procurando opção PDF...")

        pdf = page.get_by_text("PDF", exact=True)

        if await pdf.count() > 0:
            await pdf.first.click()
            print("Selecionando PDF...")
        else:
            print("PDF não encontrado diretamente.")

        await page.wait_for_timeout(1000)

        print("Executando relatório...")

        # Tenta localizar botões comuns de execução
        botoes = page.locator("button")

        quantidade = await botoes.count()

        executou = False

        for i in range(quantidade):
            try:
                texto_botao = (await botoes.nth(i).inner_text()).strip()

                if texto_botao.lower() in [
                    "execute",
                    "executar",
                    "run",
                    "generate",
                    "gerar"
                ]:
                    print("Clicando:", texto_botao)

                    async with page.expect_download(
                        timeout=60000
                    ) as download_info:

                        await botoes.nth(i).click()

                    download = await download_info.value

                    caminho = os.path.join(
                        PASTA_DOWNLOADS,
                        "_atual.pdf"
                    )

                    await download.save_as(caminho)

                    print()
                    print("Arquivo:", caminho)
                    print(
                        "Tamanho:",
                        os.path.getsize(caminho)
                    )
                    print("SUCESSO: PDF baixado corretamente.")

                    executou = True
                    break

            except Exception as e:
                print("Tentativa de botão:", e)

        if not executou:

            print()
            print("ERRO: Não foi possível identificar o botão de execução.")
            print()
            print("Texto atual da página:")
            print(texto[:5000])

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(teste())
