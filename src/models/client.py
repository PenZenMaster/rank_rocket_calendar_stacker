from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from datetime import datetime
import uuid

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    google_account_email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to OAuth credentials
    oauth_credentials = db.relationship('OAuthCredential', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'google_account_email': self.google_account_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Client {self.name}>'


class OAuthCredential(db.Model):
    __tablename__ = 'oauth_credentials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    google_client_id = db.Column(db.String(255), nullable=False)
    google_client_secret = db.Column(db.Text, nullable=False)  # Should be encrypted in production
    access_token = db.Column(db.Text)  # Should be encrypted in production
    refresh_token = db.Column(db.Text)  # Should be encrypted in production
    token_expires_at = db.Column(db.DateTime)
    scopes = db.Column(db.Text)  # JSON string of granted scopes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_valid = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'google_client_id': self.google_client_id,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'scopes': self.scopes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_valid': self.is_valid
        }
    
    def __repr__(self):
        return f'<OAuthCredential for client {self.client_id}>'


class EventCache(db.Model):
    __tablename__ = 'event_cache'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    google_event_id = db.Column(db.String(255), nullable=False)
    calendar_id = db.Column(db.String(255), nullable=False)
    event_data = db.Column(db.Text)  # JSON string of event details
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'google_event_id': self.google_event_id,
            'calendar_id': self.calendar_id,
            'event_data': self.event_data,
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
            'is_deleted': self.is_deleted
        }
    
    def __repr__(self):
        return f'<EventCache {self.google_event_id}>'

