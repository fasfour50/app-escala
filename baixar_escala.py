import asyncio
import os
from playwright.async_api import async_playwright


async def baixar_pdf_escala():
    os.makedirs("./downloads", exist_ok=True)

    async with async_playwright() as p:
        print("1. Abrindo o Chromium...")

        chromium_path = "/usr/bin/chromium"

        context = await p.chromium.launch_persistent_context(
            user_data_dir="./perfil_chrome",
            executable_path=chromium_path,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = context.pages[0] if context.pages else await context.new_page()
        page.set_default_timeout(40000)

        print("2. Acessando o I-Flight...")

        try:
            await page.goto(
                "https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage",
                wait_until="domcontentloaded",
                timeout=60000
            )
        except Exception as e:
            print(f"⚠️ Erro durante o carregamento inicial: {e}")

        await page.wait_for_timeout(5000)

        # ============================================================
        # DIAGNÓSTICO DA PÁGINA
        # ============================================================

        print("=" * 60)
        print("DIAGNÓSTICO DO NAVEGADOR")
        print("=" * 60)

        print(f"URL atual: {page.url}")

        try:
            print(f"Título: {await page.title()}")
        except Exception:
            print("Título: não foi possível obter")

        try:
            texto_pagina = await page.locator("body").inner_text()
            print("\nCONTEÚDO DA PÁGINA:")
            print(texto_pagina[:5000])
        except Exception as e:
            print(f"Não foi possível ler a página: {e}")

        print("=" * 60)

        # ============================================================
        # VERIFICA SE JÁ ESTÁ LOGADO
        # ============================================================

        print("3. Procurando Roster...")

        try:
            roster_tab = page.get_by_text("Roster", exact=True).first

            if await roster_tab.is_visible(timeout=5000):
                print("✅ Roster encontrado. Usuário aparentemente autenticado.")

            else:
                print("⚠️ Roster não está visível.")
                print("Provavelmente é necessário fazer login.")

                await context.close()
                return

        except Exception as e:
            print(f"⚠️ Não foi possível encontrar Roster: {e}")
            print("A sessão provavelmente não está autenticada.")

            await context.close()
            return

        # ============================================================
        # ACESSO AO ROSTER
        # ============================================================

        print("4. Abrindo Roster...")

        await roster_tab.hover()
        await page.wait_for_timeout(1500)

        print("5. Clicando em Roster Calendar...")

        roster_calendar = page.get_by_text(
            "Roster Calendar",
            exact=False
        ).first

        await roster_calendar.click(force=True)
        await page.wait_for_timeout(4000)

        print("6. Entrando em Roster Report...")

        roster_report = page.get_by_text(
            "Roster Report",
            exact=False
        ).first

        await roster_report.click(force=True)
        await page.wait_for_timeout(5000)

        print("7. Selecionando formato PDF...")

        select_format = page.get_by_text(
            "Select Format",
            exact=False
        ).first

        await select_format.click(force=True)
        await page.wait_for_timeout(1500)

        try:
            pdf_item = page.get_by_text(
                "pdf",
                exact=True
            ).first

            await pdf_item.click(force=True)

        except Exception:
            await page.keyboard.type("pdf")
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(1500)

        print("8. Clicando em Run...")

        try:
            async with page.expect_download(timeout=30000) as download_info:

                run_btn = page.get_by_text(
                    "Run",
                    exact=True
                ).first

                await run_btn.click(force=True)

            download = await download_info.value

            caminho_pdf = os.path.join(
                "./downloads",
                "escala_atual.pdf"
            )

            if os.path.exists(caminho_pdf):
                try:
                    os.remove(caminho_pdf)
                except Exception:
                    pass

            await download.save_as(caminho_pdf)

            print(
                f"🎉 SUCESSO! Escala baixada e salva em: {caminho_pdf}"
            )

        except Exception as e:
            print(f"❌ Erro no download: {e}")

        await context.close()


if __name__ == "__main__":
    asyncio.run(baixar_pdf_escala())
