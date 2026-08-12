import asyncio
import os
from playwright.async_api import async_playwright

URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
ESTADO = os.path.abspath("estado/_login.json")


async def main():
    print("=" * 60)
    print("TESTE DE REUTILIZAÇÃO DO LOGIN")
    print("=" * 60)

    if not os.path.exists(ESTADO):
        print("ERRO: arquivo de estado não encontrado.")
        print(ESTADO)
        raise SystemExit(1)

    print(f"Estado encontrado: {os.path.getsize(ESTADO)} bytes")

    async with async_playwright() as p:
        print("Abrindo Chromium...")

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        context = await browser.new_context(
            storage_state=ESTADO
        )

        page = await context.new_page()
        page.set_default_timeout(60000)

        print("Acessando I-Flight...")

        await page.goto(
            URL_IFLIGHT,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await page.wait_for_timeout(5000)

        print()
        print("URL atual:")
        print(page.url)

        print()
        print("Título:")
        print(await page.title())

        texto = await page.locator("body").inner_text()

        print()
        print("Verificando Roster...")

        if "Roster" in texto:
            print()
            print("=" * 60)
            print("LOGIN REUTILIZADO COM SUCESSO")
            print("Roster encontrado.")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("LOGIN NÃO FOI REUTILIZADO")
            print("Roster não encontrado.")
            print("=" * 60)

            print()
            print("URL:")
            print(page.url)

            print()
            print("Texto encontrado:")
            print(texto[:3000])

            raise SystemExit(1)

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
