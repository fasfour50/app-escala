import asyncio
import os
from playwright.async_api import async_playwright

URL = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
PASTA = r"C:\iflight\estado"
ARQUIVO = r"C:\iflight\estado\_login.json"

async def main():
    os.makedirs(PASTA, exist_ok=True)

    async with async_playwright() as p:
        print("Abrindo Chromium...")

        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("Abrindo I-Flight...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)

        print("")
        print("FAÇA O LOGIN NO NAVEGADOR.")
        print("Quando estiver dentro do I-Flight e aparecer o Roster,")
        print("volte aqui e pressione ENTER.")
        print("")

        input()

        print("Salvando estado do login...")
        await context.storage_state(path=ARQUIVO)

        print("")
        print("SUCESSO!")
        print("Arquivo:", ARQUIVO)
        print("Tamanho:", os.path.getsize(ARQUIVO), "bytes")

        await browser.close()

asyncio.run(main())
