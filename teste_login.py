```python
import asyncio
import os
from playwright.async_api import async_playwright


URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"

PERFIL = os.path.abspath("perfil_login")
ESTADO = os.path.abspath("estado_login.json")


async def main():

    print("=" * 60)
    print("TESTE DE LOGIN I-FLIGHT")
    print("=" * 60)

    os.makedirs(PERFIL, exist_ok=True)

    async with async_playwright() as p:

        print("Abrindo Chromium...")

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PERFIL,
            executable_path="/usr/bin/chromium",
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()

        page.set_default_timeout(60000)

        print("Acessando I-Flight...")

        await page.goto(
            URL_IFLIGHT,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print()
        print("URL atual:")
        print(page.url)

        print()
        print("=" * 60)
        print("FAÇA O LOGIN MANUALMENTE")
        print("=" * 60)
        print()
        print("Complete o login Google e o Authenticator.")
        print("Depois que o I-Flight estiver aberto,")
        print("volte ao terminal.")
        print()

        input("Pressione ENTER depois de concluir o login...")

        print()
        print("Verificando sessão...")

        await page.wait_for_timeout(3000)

        print("URL após login:")
        print(page.url)

        # Salva cookies + localStorage
        await browser.storage_state(path=ESTADO)

        print()
        print("=" * 60)
        print("SESSÃO SALVA")
        print("=" * 60)
        print()
        print(f"Arquivo: {ESTADO}")

        if os.path.exists(ESTADO):
            tamanho = os.path.getsize(ESTADO)
            print(f"Tamanho: {tamanho} bytes")
        else:
            print("ERRO: estado não foi criado.")

        print()
        print("Fechando navegador...")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
```
