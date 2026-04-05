"""
Elimina correos de spam y promociones de Gmail.
Primera vez abrirá el navegador para autorizar.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://mail.google.com/']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token_spam.json')

# Qué borrar — puedes añadir o quitar líneas
QUERIES = [
    "before:2024/12/01",  # absolutamente todo antes de diciembre 2024
]


def autenticar():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


def borrar_por_query(service, query):
    total = 0
    print(f"\n🔍 Buscando: {query}")
    while True:
        res = service.users().messages().list(userId='me', q=query, maxResults=500).execute()
        mensajes = res.get('messages', [])
        if not mensajes:
            break
        ids = [m['id'] for m in mensajes]
        service.users().messages().batchDelete(userId='me', body={'ids': ids}).execute()
        total += len(ids)
        print(f"   ✓ {total} eliminados...")
    print(f"   Total '{query}': {total}")
    return total


def main():
    creds = autenticar()
    service = build('gmail', 'v1', credentials=creds)

    total_global = 0
    for q in QUERIES:
        total_global += borrar_por_query(service, q)

    print(f"\n✅ Listo. {total_global} correos eliminados en total.")


if __name__ == "__main__":
    main()
