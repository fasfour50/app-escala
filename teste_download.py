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

        print("Verificando Roster...")

        texto = await page.locator("body").inner_text()

        if "Roster" not in texto:
            print("ERRO: Roster não encontrado.")
            print(texto[:5000])
            await browser.close()
            return

        print("OK: Roster encontrado.")

        roster = page.get_by_text(
            "Roster",
            exact=True
        )

        await roster.first.click()

        await page.wait_for_timeout(3000)

        print("Abrindo Roster Calendar...")

        calendar = page.get_by_text(
            "Roster Calendar",
            exact=True
        )

        await calendar.first.click()

        await page.wait_for_timeout(3000)

        print("Abrindo Roster Report...")

        report = page.get_by_text(
            "Roster Report",
            exact=True
        )

        await report.first.click()

        await page.wait_for_timeout(3000)

        await salvar_debug(
            page,
            "debug_relatorio"
        )

        print()
        print("=== CAMPOS SELECT ===")

        selects = page.locator("select")

        quantidade_selects = await selects.count()

        print(
            "Quantidade de SELECTs:",
            quantidade_selects
        )

        for i in range(quantidade_selects):

            try:

                select = selects.nth(i)

                print()
                print(
                    f"SELECT {i}"
                )

                print(
                    "Nome:",
                    await select.get_attribute("name")
                )

                print(
                    "ID:",
                    await select.get_attribute("id")
                )

                print(
                    "Classe:",
                    await select.get_attribute("class")
                )

                print(
                    "Valor:",
                    await select.input_value()
                )

                opcoes = select.locator("option")

                quantidade_opcoes = await opcoes.count()

                print(
                    "Opções:",
                    quantidade_opcoes
                )

                for j in range(quantidade_opcoes):

                    option = opcoes.nth(j)

                    print(
                        f"  [{j}]",
                        await option.inner_text(),
                        "| valor:",
                        await option.get_attribute("value")
                    )

            except Exception as e:

                print(
                    "Erro lendo SELECT:",
                    e
                )

        print()
        print("=== INPUTS ===")

        inputs = page.locator("input")

        quantidade_inputs = await inputs.count()

        print(
            "Quantidade de INPUTs:",
            quantidade_inputs
        )

        for i in range(quantidade_inputs):

            try:

                elemento = inputs.nth(i)

                print()
                print(
                    f"INPUT {i}"
                )

                print(
                    "Tipo:",
                    await elemento.get_attribute("type")
                )

                print(
                    "Nome:",
                    await elemento.get_attribute("name")
                )

                print(
                    "ID:",
                    await elemento.get_attribute("id")
                )

                print(
                    "Valor:",
                    await elemento.get_attribute("value")
                )

                print(
                    "Placeholder:",
                    await elemento.get_attribute("placeholder")
                )

            except Exception as e:

                print(
                    "Erro lendo INPUT:",
                    e
                )

        print()
        print("=== ELEMENTOS COM TEXTO SELECT FORMAT ===")

        elementos = page.get_by_text(
            "Select Format",
            exact=False
        )

        quantidade = await elementos.count()

        print(
            "Quantidade:",
            quantidade
        )

        for i in range(quantidade):

            try:

                elemento = elementos.nth(i)

                print()
                print(
                    "Elemento:",
                    i
                )

                print(
                    "Tag:",
                    await elemento.evaluate(
                        "(el) => el.tagName"
                    )
                )

                print(
                    "HTML:",
                    (await elemento.evaluate(
                        "(el) => el.outerHTML"
                    ))[:3000]
                )

            except Exception as e:

                print(
                    "Erro:",
                    e
                )

        print()
        print("=== BOTÕES ===")

        botoes = page.locator("button")

        quantidade = await botoes.count()

        for i in range(quantidade):

            try:

                texto_botao = (
                    await botoes.nth(i).inner_text()
                ).strip()

                if texto_botao:

                    print(
                        f"BOTÃO {i}: [{texto_botao}]"
                    )

            except Exception:
                pass

        print()
        print("Diagnóstico concluído.")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(teste())
