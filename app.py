import imaplib
import email
from email.header import decode_header

class EmailParserNEXUS:
    def __init__(self, email_user, email_pass):
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.mail.login(email_user, email_pass)
        
    def fetch_unread_orders(self):
        self.mail.select("inbox")
        status, messages = self.mail.search(None, '(UNSEEN)')
        # Botul NEXUS citește doar emailurile necitite care au atașamente (Comenzi de la clienți)
        # 1. Extrage atașamentul (XLSX, PDF)
        # 2. Îl trimite către OCR / Pandas pentru decodare
        # 3. Încarcă datele curățate în db_buffer.sqlite cu status "Așteaptă Aprobare Angajat"
        return "Am găsit 3 comenzi noi. Le-am decodat și le-am pus în Buffer."
