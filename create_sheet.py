#!/usr/bin/env python3
"""
Cria (ou atualiza) a planilha de acompanhamento de testes A/B no Google Sheets.
Uso: python create_sheet.py
"""

import csv
import os
import sys
from pathlib import Path

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TRACKING_CSV = "tracking_results.csv"
SHEET_NAME = "Meliuz - Acompanhamento de Testes A/B"
TOKEN_FILE = "token.json"


def get_credentials(credentials_file: str) -> Credentials:
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.valid:
            return creds

    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    return creds


def find_credentials_file() -> str:
    for f in Path(".").glob("client_secret*.json"):
        return str(f)
    for f in Path(".").glob("credentials*.json"):
        return str(f)
    raise FileNotFoundError("Arquivo de credenciais OAuth nao encontrado na pasta.")


def load_tracking_csv(filepath: str) -> tuple[list, list[list]]:
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    headers = rows[0]
    data = rows[1:]
    return headers, data


def main():
    print("[1/4] Localizando credenciais...")
    creds_file = find_credentials_file()
    print(f"      Usando: {creds_file}")

    print("[2/4] Autenticando com Google (abrira o browser)...")
    creds = get_credentials(creds_file)
    gc = gspread.authorize(creds)
    print("      Autenticado.")

    print("[3/4] Criando planilha no Google Sheets...")
    try:
        sh = gc.open(SHEET_NAME)
        print(f"      Planilha ja existe — atualizando.")
        ws = sh.sheet1
        ws.clear()
    except gspread.SpreadsheetNotFound:
        sh = gc.create(SHEET_NAME)
        ws = sh.sheet1
        print(f"      Planilha criada.")

    headers, data = load_tracking_csv(TRACKING_CSV)
    all_rows = [headers] + data
    ws.update(all_rows, "A1")

    # Formatar cabecalho em negrito
    ws.format("A1:J1", {"textFormat": {"bold": True}})

    # Compartilhar publicamente com leitura
    sh.share(None, perm_type="anyone", role="reader")

    sheet_url = f"https://docs.google.com/spreadsheets/d/{sh.id}"
    print(f"[4/4] Pronto!\n")
    print(f"      URL da planilha: {sheet_url}")
    print(f"      Acesso publico de leitura ativado.")
    print(f"\n      Guarde essa URL para incluir no README e no email de entrega.")
    return sheet_url


if __name__ == "__main__":
    main()
