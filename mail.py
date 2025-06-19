import os
import asyncio
import email
import smtplib
import gnupg
from email.mime.text import MIMEText
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
import argparse

# Configuration
GPG_HOME = os.path.expanduser("~/.gnupg")
MAILBOX_DIR = os.path.expanduser("~/secure_mailbox")
SMTP_LISTEN_HOST = "127.0.0.1"
SMTP_LISTEN_PORT = 1025

os.makedirs(MAILBOX_DIR, exist_ok=True)
gpg = gnupg.GPG(gnupghome=GPG_HOME)

# Helper functions
def encrypt_message(recipient, message):
    encrypted_data = gpg.encrypt(message, recipients=[recipient])
    if not encrypted_data.ok:
        raise Exception(f"GPG encryption failed: {encrypted_data.status}")
    return str(encrypted_data)

def decrypt_message(encrypted_message):
    decrypted_data = gpg.decrypt(encrypted_message)
    if not decrypted_data.ok:
        raise Exception(f"GPG decryption failed: {decrypted_data.status}")
    return str(decrypted_data)

def save_mail(recipient, encrypted_message):
    mailbox = os.path.join(MAILBOX_DIR, recipient)
    os.makedirs(mailbox, exist_ok=True)
    idx = len(os.listdir(mailbox))
    with open(os.path.join(mailbox, f"{idx}.eml"), "w") as f:
        f.write(encrypted_message)

def load_mail(recipient):
    mailbox = os.path.join(MAILBOX_DIR, recipient)
    if not os.path.exists(mailbox):
        return []
    mails = []
    for fname in sorted(os.listdir(mailbox)):
        with open(os.path.join(mailbox, fname), "r") as f:
            mails.append(f.read())
    return mails

# SMTP Handler
class EncryptedMailHandler(AsyncMessage):
    async def handle_message(self, message):
        to_addr = message["To"]
        from_addr = message["From"]
        payload = message.get_payload(decode=True).decode()
        encrypted = encrypt_message(to_addr, payload)
        save_mail(to_addr, encrypted)
        print(f"Encrypted mail saved for {to_addr} from {from_addr}")

# SMTP Server
def start_smtp_server():
    handler = EncryptedMailHandler()
    controller = Controller(handler, hostname=SMTP_LISTEN_HOST, port=SMTP_LISTEN_PORT)
    controller.start()
    print(f"SMTP server running at {SMTP_LISTEN_HOST}:{SMTP_LISTEN_PORT}")
    return controller

# Sending email
def send_encrypted_mail(smtp_host, smtp_port, sender, recipient, subject, body):
    encrypted_body = encrypt_message(recipient, body)
    msg = MIMEText(encrypted_body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.send_message(msg)
    print(f"Encrypted email sent from {sender} to {recipient}")

# Receiving email (decrypting)
def receive_and_decrypt_mail(recipient):
    encrypted_mails = load_mail(recipient)
    decrypted_mails = []
    for eml in encrypted_mails:
        try:
            decrypted = decrypt_message(eml)
            decrypted_mails.append(decrypted)
        except Exception as e:
            decrypted_mails.append(f"Failed to decrypt: {e}")
    return decrypted_mails


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Sentinel Secure End-to-End Encrypted Mail Server")
    parser.add_argument("--serve", action="store_true", help="Start SMTP server")
    parser.add_argument("--send", nargs=5, metavar=("SMTP_HOST", "SMTP_PORT", "SENDER", "RECIPIENT", "SUBJECT_BODY"), help="Send encrypted mail")
    parser.add_argument("--inbox", metavar="RECIPIENT", help="Show and decrypt inbox for recipient")
    args = parser.parse_args()

    if args.serve:
        start_smtp_server()
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print("Server stopped.")
    elif args.send:
        smtp_host, smtp_port, sender, recipient, subject_body = args.send
        subject, body = subject_body.split(":", 1)
        send_encrypted_mail(smtp_host, int(smtp_port), sender, recipient, subject, body)
    elif args.inbox:
        mails = receive_and_decrypt_mail(args.inbox)
        for idx, mail in enumerate(mails):
            print(f"--- Mail #{idx+1} ---\n{mail}\n")
    else:
        parser.print_help()