import subprocess
import os
import sys

PASTA = r"C:\iflight"

print("=" * 50)
print("ATUALIZANDO ESCALA")
print("=" * 50)

# 1. Baixa o PDF e gera o painel
resultado = subprocess.run(
    [sys.executable, os.path.join(PASTA, "atualizar_escala.py")],
    cwd=PASTA
)

if resultado.returncode != 0:
    print()
    print("ERRO ao atualizar a escala.")
    input("Pressione ENTER para fechar...")
    sys.exit(resultado.returncode)

print()
print("=" * 50)
print("ABRINDO PAINEL")
print("=" * 50)

# 2. Inicia o Streamlit
subprocess.run(
    [sys.executable, "-m", "streamlit", "run", os.path.join(PASTA, "app.py")],
    cwd=PASTA
)
