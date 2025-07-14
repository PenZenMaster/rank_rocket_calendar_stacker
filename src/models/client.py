from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    oauth_credentials = relationship(
        "OAuthCredential",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<Client {self.name}>"


class OAuthCredential(db.Model):
    __tablename__ = "oauth_credentials"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    google_client_id = Column(String(255), nullable=False)
    google_client_secret = Column(String(255), nullable=False)
    access_token = Column(String(500), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    scopes = Column(String(1000), nullable=True)

    client = relationship("Client", back_populates="oauth_credentials")

    def __repr__(self):
        return f"<OAuthCredential for Client ID: {self.client_id}>"
