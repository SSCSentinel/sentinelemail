import os
import uuid as uuid_lib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import BINARY
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from sqlalchemy import (
    create_engine, Column, Integer, String, LargeBinary, Enum, ForeignKey
)

Base = declarative_base()

# Securely load encryption key from environment variable
ENCRYPTION_KEY = os.environ.get("EMAIL_DB_ENCRYPTION_KEY")
if not ENCRYPTION_KEY or len(ENCRYPTION_KEY) < 32:
    raise ValueError("EMAIL_DB_ENCRYPTION_KEY must be set to a 32-byte base64 string.")

ENCRYPTION_KEY = ENCRYPTION_KEY.encode()[:32]  # Use only 32 bytes

def encrypt_content(plain_text: str) -> bytes:
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plain_text.encode(), None)
    return nonce + ct

def decrypt_content(cipher_text: bytes) -> str:
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = cipher_text[:12]
    ct = cipher_text[12:]
    return aesgcm.decrypt(nonce, ct, None).decode()

class EmailMessage(Base):
    __tablename__ = 'email_messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, index=True)
    uuid = Column(String(36), nullable=False, unique=True, default=lambda: str(uuid_lib.uuid4()))
    direction = Column(Integer, nullable=False)  # 1: incoming, 2: sent, 3: failed
    encrypted_content = Column(LargeBinary, nullable=True)  # Only for incoming mail

    def set_content(self, plain_text: str):
        self.encrypted_content = encrypt_content(plain_text)

    def get_content(self) -> str:
        if self.encrypted_content:
            return decrypt_content(self.encrypted_content)
        return None

DATABASE_URL = os.environ.get("AIVEN_MYSQL_URL")
if not DATABASE_URL:
    raise ValueError("AIVEN_MYSQL_URL must be set in environment variables.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

# Not for production use, for testing purposes only
if __name__ == "__main__":
    init_db()
    session = SessionLocal()
    try:
        # Store an incoming email
        email = EmailMessage(username="alice", direction=1)
        email.set_content("Hello Alice, this is a secure message.")
        session.add(email)
        session.commit()

        # Retrieve and decrypt
        stored = session.query(EmailMessage).filter_by(username="alice").first()
        print(stored.get_content())
    finally:
        session.close()