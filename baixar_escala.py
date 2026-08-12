import asyncio
import os
from playwright.async_api import async_playwright

async def baixar_pdf_escala():
    os.makedirs("./downloads", exist_ok=True)
    
    async with async_playwright() as p:
        print("1. Abrindo o navegador...")
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
        await page.goto("https://iflightla.ibsplc.aero/iflight-crew/web/getMainPage")
        await page.wait_for_timeout(4000)
        
        # Tratamento para pop-up de instabilidade do servidor
        try:
            ok_btn = page.get_by_role("button", name="OK").first
            if await ok_btn.is_visible():
                print("⚠️ Pop-up de erro detectado! Recarregando página...")
                await ok_btn.click()
                await page.wait_for_timeout(1000)
                await page.reload()
                await page.wait_for_timeout(5000)
        except Exception:
            pass
        
        print("3. Abrindo Roster...")
        roster_tab = page.get_by_text("Roster", exact=True).first
        await roster_tab.hover()
        await page.wait_for_timeout(1500)
        
        print("4. Clicando em Roster Calendar...")
        roster_calendar = page.get_by_text("Roster Calendar", exact=False).first
        await roster_calendar.click(force=True)
        await page.wait_for_timeout(4000)
        
        print("5. Entrando em Roster Report...")
        roster_report = page.get_by_text("Roster Report", exact=False).first
        await roster_report.click(force=True)
        await page.wait_for_timeout(5000)
        
        print("6. Selecionando formato 'pdf'...")
        select_format = page.get_by_text("Select Format", exact=False).first
        await select_format.click(force=True)
        await page.wait_for_timeout(1500)
        
        try:
            pdf_item = page.get_by_text("pdf", exact=True).first
            await pdf_item.click(force=True)
        except Exception:
            await page.keyboard.type("pdf")
            await page.keyboard.press("Enter")

        await page.wait_for_timeout(1500)
        
        print("7. Clicando em 'Run'...")
        try:
            async with page.expect_download(timeout=30000) as download_info:
                run_btn = page.get_by_text("Run", exact=True).first
                await run_btn.click(force=True)
                
            download = await download_info.value
            caminho_pdf = os.path.join("./downloads", "escala_atual.pdf")
            
            # Remove o arquivo antigo antes de salvar o novo para evitar Permission Denied
            if os.path.exists(caminho_pdf):
                try:
                    os.remove(caminho_pdf)
                except Exception:
                    pass

            await download.save_as(caminho_pdf)
            print(f"\n🎉 SUCESSO! Escala baixada e salva em: {caminho_pdf}")
            
        except Exception as e:
            print(f"\n❌ Erro no download: {e}")
            input("Pressione ENTER para fechar...")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(baixar_pdf_escala())
