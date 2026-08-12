import pdfplumber
import os
import re
from datetime import datetime, timedelta

MESES_MAP = {
    'JAN': 'Jan', 'FEB': 'Feb', 'MAR': 'Mar', 'APR': 'Apr',
    'MAY': 'May', 'JUN': 'Jun', 'JUL': 'Jul', 'AUG': 'Aug',
    'SEP': 'Sep', 'OCT': 'Oct', 'NOV': 'Nov', 'DEC': 'Dec'
}

def normalizar_data(data_raw):
    if not data_raw:
        return None
    limpo = re.sub(r'[^a-zA-Z0-9]', ' ', data_raw).strip()
    match = re.search(r'(\d{1,2})\s*([a-zA-Z]{3})\s*(\d{4})?', limpo)
    if match:
        dia, mes, ano = match.groups()
        dia = dia.zfill(2)
        mes = mes.upper()[:3]
        ano = ano if ano else "2026"
        if mes in MESES_MAP:
            return f"{dia}-{MESES_MAP[mes]}-{ano}"
    return None

def extrair_dados_pdf(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        print(f"âŒ Arquivo '{caminho_pdf}' nÃ£o encontrado.")
        return []

    eventos = []
    data_atual = None

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue
            
            linhas = texto.split("\n")
            
            for linha in linhas:
                l = linha.strip()
                if not l or "Pairing" in l or "Roster Report" in l:
                    continue

                linha_limpa = re.sub(r'\d{2}-[A-Za-z]{3}-\d{4}\s+\d{2}\.\d{2}\s*$', '', l)

                match_data = re.match(r'^(\d{2}[-\s]?[A-Za-z]{3}[-\s]?\d{0,4})', linha_limpa)
                if match_data:
                    dt = normalizar_data(match_data.group(1))
                    if dt:
                        data_atual = dt

                if not data_atual:
                    continue

                if re.search(r'\b(DO|OFF)\b', linha_limpa):
                    if not any(e['data'] == data_atual and e['tipo'] == 'FOLGA' for e in eventos):
                        eventos.append({"tipo": "FOLGA", "data": data_atual, "ordem": len(eventos)})
                    continue

                # ExtraÃ§Ã£o correta do HSB com intervalo exato (ex: 03:30-04:48)
                match_solo = re.search(r'\b(HSB|HSBE|RES|RESE|SBY|SBYE|STBY|TRN|OFC|SIM|MCK320)\b', linha_limpa)
                if match_solo:
                    codigo_act = match_solo.group(1)
                    horas_solo = re.findall(r'\b(\d{2}:\d{2})\b', linha_limpa)
                    
                    hora_str = ""
                    if len(horas_solo) >= 2:
                        hora_str = f"{horas_solo[0]}-{horas_solo[1]}"
                    elif len(horas_solo) == 1:
                        hora_str = horas_solo[0]

                    ev_solo = {
                        "tipo": "SOBREAVISO",
                        "data": data_atual,
                        "codigo": codigo_act,
                        "horario": hora_str,
                        "ordem": len(eventos)
                    }
                    if ev_solo not in eventos:
                        eventos.append(ev_solo)

                # ExtraÃ§Ã£o correta para APZ/Duty capturando linhas de apresentaÃ§Ã£o isoladas
                is_apz_line = re.search(r'\b(APZ|RPT)\b', linha_limpa) or (match_solo is None and re.search(r'^\d{2}[-\s]?[A-Za-z]{3}', linha_limpa))
                duty_match = re.search(r'\b(\d{2}:\d{2})\b', linha_limpa)

                if duty_match and is_apz_line and not match_solo:
                    hora_duty = duty_match.group(1)
                    if not re.search(r'\bLA\d{3,4}\b', linha_limpa) and not any(e['data'] == data_atual and e['tipo'] == 'DUTY' and e['hora'] == hora_duty for e in eventos):
                        eventos.append({
                            "tipo": "DUTY", 
                            "data": data_atual, 
                            "hora": hora_duty,
                            "ordem": len(eventos)
                        })

                voos_na_linha = re.findall(r'\b(LA\d{3,4})\b', linha_limpa)
                trechos = re.findall(r'([A-Z]{3})\s+(\d{2}:\d{2})', linha_limpa)
                eqp_match = re.search(r'\b(32S|320|31R|789|773)\b', linha_limpa)
                equipamento = eqp_match.group(1) if eqp_match else ""

                if voos_na_linha and trechos:
                    voo_code = voos_na_linha[0]
                    dep_stn, dep_time, arr_stn, arr_time = "", "", "", ""

                    if len(trechos) >= 2:
                        dep_stn, dep_time = trechos[0]
                        arr_stn, arr_time = trechos[1]
                    elif len(trechos) == 1:
                        arr_stn, arr_time = trechos[0]

                    nova_etapa = {
                        "tipo": "VOO",
                        "data": data_atual,
                        "voo": voo_code,
                        "dep_stn": dep_stn,
                        "dep_time": dep_time,
                        "arr_stn": arr_stn,
                        "arr_time": arr_time,
                        "eqp": equipamento,
                        "ordem": len(eventos)
                    }
                    if nova_etapa not in eventos:
                        eventos.append(nova_etapa)

    return eventos

def gerar_escala_html(eventos):
    escala_por_dia = {}
    for ev in eventos:
        try:
            dt_obj = datetime.strptime(ev['data'], "%d-%b-%Y").date()
        except ValueError:
            continue
            
        if dt_obj not in escala_por_dia:
            escala_por_dia[dt_obj] = []
        escala_por_dia[dt_obj].append(ev)

    if not escala_por_dia:
        print("âš ï¸ Nenhum evento extraÃ­do do PDF.")
        return None

    min_date = min(escala_por_dia.keys())
    max_date = max(escala_por_dia.keys())

    datas_exibicao = []
    curr = min_date
    while curr <= max_date:
        datas_exibicao.append(curr)
        curr += timedelta(days=1)

    data_hoje = datetime.now().date()

    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Escala AIMS</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 10px;
                color: #000;
            }
            .app-bar {
                background-color: #2b2361;
                color: #fff;
                padding: 12px 16px;
                font-size: 1.25rem;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-radius: 4px 4px 0 0;
            }
            .container {
                max-width: 100%;
                overflow-x: auto;
                background: #fff;
                border: 1px solid #ccc;
            }
            .aims-grid {
                display: flex;
                width: max-content;
                min-width: 100%;
            }
            .day-column {
                width: 75px;
                min-width: 75px;
                border-right: 1px solid #ccc;
                display: flex;
                flex-direction: column;
                background: #fbeae9;
            }
            .day-column.off-day {
                background: #e8f5e9;
            }
            .day-column.today-highlight {
                background: #fff8e1 !important;
            }
            .day-header {
                text-align: center;
                padding: 6px 2px;
                border-bottom: 1px solid #ccc;
                font-weight: bold;
                font-size: 0.95em;
                color: #000;
                line-height: 1.1;
                background-color: #f1f3f5;
            }
            .day-column.off-day .day-header {
                background-color: #e8f5e9;
            }
            .day-column.today-highlight .day-header {
                background-color: #ffecb3 !important;
            }
            .day-content {
                padding: 6px 2px;
                font-size: 1.0em;
                text-align: center;
                line-height: 1.2;
                flex-grow: 1;
            }
            .duty-rpt {
                font-weight: normal;
                font-size: 1.0em;
                color: #000;
                margin-bottom: 8px;
                padding-bottom: 4px;
                border-bottom: 1px solid #ccc;
            }
            .flight-card {
                margin-bottom: 10px;
            }
            .flight-num {
                display: block;
                font-weight: bold;
                font-size: 1.05em;
                margin-bottom: 2px;
                line-height: 1.1;
            }
            .flight-time {
                font-size: 1.0em;
                font-weight: normal;
                color: #333;
            }
            .flight-stn {
                font-weight: normal;
                font-size: 1.0em;
                color: #333;
                margin: 1px 0;
            }
            .flight-eqp {
                font-size: 0.95em;
                font-weight: normal;
                color: #555;
                margin-top: 1px;
            }
            .continuation-tag {
                font-weight: bold;
                font-size: 1.05em;
                color: #000;
                margin-bottom: 4px;
            }
            .off-text {
                font-weight: bold;
                font-size: 1.1em;
                color: #2b8a3e;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="app-bar">
            <span>â† Escala AIMS</span>
        </div>
        <div class="container">
            <div class="aims-grid">
    """

    for idx, dt in enumerate(datas_exibicao):
        header_str = dt.strftime("%d%b<br>%a")
        eventos_dia = escala_por_dia.get(dt, [])
        eventos_dia.sort(key=lambda x: x.get('ordem', 0))

        is_off = any(e["tipo"] == "FOLGA" for e in eventos_dia)
        is_today = (dt == data_hoje)

        classes_col = ["day-column"]
        if is_off:
            classes_col.append("off-day")
        if is_today:
            classes_col.append("today-highlight")
        
        col_class_str = " ".join(classes_col)

        html_content += f"""
        <div class="{col_class_str}">
            <div class="day-header">{header_str}</div>
            <div class="day-content">
        """
        
        if is_off:
            html_content += '<div class="off-text">OFF</div>'
        else:
            for ev in eventos_dia:
                if ev["tipo"] == "DUTY":
                    html_content += f'<div class="duty-rpt">APZ<br>{ev["hora"]}</div>'
                elif ev["tipo"] == "SOBREAVISO":
                    html_content += f"""
                    <div class="flight-card">
                        <div class="flight-num">{ev['codigo']}</div>
                        <div class="flight-time">{ev['horario']}</div>
                    </div>
                    """
                elif ev["tipo"] == "VOO":
                    v_split = ev['voo'].replace('LA', 'LA<br>')
                    html_content += f"""
                    <div class="flight-card">
                        <div class="flight-num">{v_split}</div>
                        <div class="flight-time">{ev['dep_time']}</div>
                        <div class="flight-stn">{ev['dep_stn']}</div>
                        <div class="flight-stn">{ev['arr_stn']}</div>
                        <div class="flight-time">{ev['arr_time']}</div>
                        {f'<div class="flight-eqp">({ev["eqp"]})</div>' if ev["eqp"] else ''}
                    </div>
                    """

            voos_hoje = [e for e in eventos_dia if e["tipo"] == "VOO"]
            if not voos_hoje and not any(e["tipo"] == "SOBREAVISO" for e in eventos_dia):
                dt_ant = dt - timedelta(days=1)
                dt_prox = dt + timedelta(days=1)
                
                eventos_ant = escala_por_dia.get(dt_ant, [])
                eventos_prox = escala_por_dia.get(dt_prox, [])
                
                voos_ant = [e for e in eventos_ant if e["tipo"] == "VOO"]
                voos_prox = [e for e in eventos_prox if e["tipo"] == "VOO"]
                
                if voos_ant and voos_prox:
                    ultimo_pouso = voos_ant[-1]
                    primeiro_voo_prox = voos_prox[0]
                    
                    stn_layover = ultimo_pouso['arr_stn']
                    eqp_layover = primeiro_voo_prox.get('eqp') or ultimo_pouso.get('eqp') or '31R'
                    
                    html_content += f"""
                    <div class="flight-card">
                        <div class="continuation-tag">(...)</div>
                        <div class="flight-stn">{stn_layover}</div>
                        <div class="flight-time">{ultimo_pouso['arr_time']}</div>
                        <div class="flight-time">00:00</div>
                        <div class="flight-eqp">({eqp_layover})</div>
                    </div>
                    """

        html_content += """
            </div>
        </div>
        """

    html_content += """
            </div>
        </div>
    </body>
    </html>
    """

    caminho_html = os.path.abspath("minha_escala.html")
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    return caminho_html

if __name__ == "__main__":
    caminho_pdf = os.path.join("downloads", "escala_atual.pdf")
    evs = extrair_dados_pdf(caminho_pdf)
    caminho_html = gerar_escala_html(evs)
    if caminho_html:
        print(f"âœ… HTML gerado com sucesso: {caminho_html}")
        os.system(f'start "" "{caminho_html}"')
