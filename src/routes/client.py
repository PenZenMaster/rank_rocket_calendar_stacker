from flask import Blueprint, request, jsonify
from src.models.client import db, Client, OAuthCredential
from datetime import datetime

client_bp = Blueprint('client', __name__)

@client_bp.route('/clients', methods=['GET'])
def get_clients():
    """Get all clients"""
    try:
        clients = Client.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [client.to_dict() for client in clients]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/clients/<client_id>', methods=['GET'])
def get_client(client_id):
    """Get a specific client by ID"""
    try:
        client = Client.query.get_or_404(client_id)
        return jsonify({
            'success': True,
            'data': client.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/clients', methods=['POST'])
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'google_account_email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if email already exists
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            return jsonify({
                'success': False,
                'error': 'Client with this email already exists'
            }), 400
        
        # Check if Google account email already exists
        existing_google_account = Client.query.filter_by(google_account_email=data['google_account_email']).first()
        if existing_google_account:
            return jsonify({
                'success': False,
                'error': 'Client with this Google account already exists'
            }), 400
        
        # Create new client
        client = Client(
            name=data['name'],
            email=data['email'],
            google_account_email=data['google_account_email']
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': client.to_dict(),
            'message': 'Client created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/clients/<client_id>', methods=['PUT'])
def update_client(client_id):
    """Update an existing client"""
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            client.name = data['name']
        if 'email' in data:
            # Check if new email already exists (excluding current client)
            existing_client = Client.query.filter(
                Client.email == data['email'],
                Client.id != client_id
            ).first()
            if existing_client:
                return jsonify({
                    'success': False,
                    'error': 'Another client with this email already exists'
                }), 400
            client.email = data['email']
        if 'google_account_email' in data:
            # Check if new Google account email already exists (excluding current client)
            existing_google_account = Client.query.filter(
                Client.google_account_email == data['google_account_email'],
                Client.id != client_id
            ).first()
            if existing_google_account:
                return jsonify({
                    'success': False,
                    'error': 'Another client with this Google account already exists'
                }), 400
            client.google_account_email = data['google_account_email']
        if 'is_active' in data:
            client.is_active = data['is_active']
        
        client.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': client.to_dict(),
            'message': 'Client updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Soft delete a client (mark as inactive)"""
    try:
        client = Client.query.get_or_404(client_id)
        client.is_active = False
        client.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Client deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/clients/<client_id>/oauth', methods=['GET'])
def get_client_oauth(client_id):
    """Get OAuth credentials for a client"""
    try:
        client = Client.query.get_or_404(client_id)
        oauth_creds = OAuthCredential.query.filter_by(client_id=client_id, is_valid=True).first()
        
        if not oauth_creds:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No OAuth credentials found for this client'
            }), 200
        
        return jsonify({
            'success': True,
            'data': oauth_creds.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

