import asyncio
import os
from playwright.async_api import async_playwright

URL_IFLIGHT = "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage"

PASTA_PERFIL = os.path.abspath("perfil_login")
ARQUIVO_ESTADO = os.path.abspath("estado_login.json")


async def main():

    print("=" * 60)
    print("TESTE DE LOGIN I-FLIGHT")
    print("=" * 60)

    os.makedirs(PASTA_PERFIL, exist_ok=True)

    async with async_playwright() as p:

        print("Abrindo navegador...")

        context = await p.chromium.launch_persistent_context(
            user_data_dir=PASTA_PERFIL,
            headless=False,
            viewport={"width": 1400, "height": 900},
        )

        page = context.pages[0] if context.pages else await context.new_page()

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
        print("=" * 60)
        print("FAÇA O LOGIN MANUALMENTE")
        print("=" * 60)
        print("1. Entre com sua conta Google")
        print("2. Faça a autenticação pelo Authenticator")
        print("3. Aguarde o I-Flight carregar completamente")
        print("4. Confirme que você consegue visualizar o Roster")
        print("5. Volte para esta janela")
        print()

        input("Pressione ENTER somente depois que estiver dentro do I-Flight...")

        await page.wait_for_timeout(3000)

        print()
        print("URL depois do login:")
        print(page.url)

        await context.storage_state(path=ARQUIVO_ESTADO)

        print()
        print("=" * 60)
        print("ESTADO DA SESSÃO SALVO")
        print("=" * 60)
        print(f"Arquivo: {ARQUIVO_ESTADO}")

        if os.path.exists(ARQUIVO_ESTADO):

            tamanho = os.path.getsize(ARQUIVO_ESTADO)

            print(f"Tamanho: {tamanho} bytes")

            if tamanho == 0:
                raise Exception("O arquivo de estado ficou vazio.")

        else:

            raise Exception(
                "O arquivo estado_login.json não foi criado."
            )

        print()
        print("Teste concluído.")
        print("Não envie estado_login.json para o GitHub.")

        await context.close()


if __name__ == "__main__":
    asyncio.run(main())

