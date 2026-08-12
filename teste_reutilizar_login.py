import asyncio
from playwright.async_api import async_playwright

URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"
ARQUIVO_ESTADO = r"C:\iflight\estado_login.json"

async def main():
    print("=" * 60)
    print("TESTE DE REUTILIZAÇÃO DO LOGIN")
    print("=" * 60)

    async with async_playwright() as p:
        print("Abrindo Chromium com o estado salvo...")

        browser = await p.chromium.launch(
            headless=False
        )

        context = await browser.new_context(
            storage_state=ARQUIVO_ESTADO
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
            print("Texto encontrado:")
            print(texto[:5000])

        print()
        print("Pressione ENTER para fechar o navegador.")

        input()

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
