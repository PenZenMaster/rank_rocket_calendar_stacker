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


@client_bp.route('/oauth', methods=['GET'])
def get_all_oauth():
    """Get all OAuth credentials"""
    try:
        oauth_creds = OAuthCredential.query.filter_by(is_valid=True).all()
        return jsonify({
            'success': True,
            'data': [cred.to_dict() for cred in oauth_creds]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/oauth', methods=['POST'])
def create_oauth_credentials():
    """Create new OAuth credentials for a client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['client_id', 'google_client_id', 'google_client_secret']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Verify client exists
        client = Client.query.get(data['client_id'])
        if not client:
            return jsonify({
                'success': False,
                'error': 'Client not found'
            }), 404
        
        # Check if OAuth credentials already exist for this client
        existing_oauth = OAuthCredential.query.filter_by(
            client_id=data['client_id'], 
            is_valid=True
        ).first()
        if existing_oauth:
            return jsonify({
                'success': False,
                'error': 'OAuth credentials already exist for this client'
            }), 400
        
        # Create new OAuth credentials
        oauth_creds = OAuthCredential(
            client_id=data['client_id'],
            google_client_id=data['google_client_id'],
            google_client_secret=data['google_client_secret'],  # In production, encrypt this
            scopes=data.get('scopes', 'https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/calendar.events')
        )
        
        db.session.add(oauth_creds)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': oauth_creds.to_dict(),
            'message': 'OAuth credentials created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/oauth/<oauth_id>', methods=['PUT'])
def update_oauth_credentials(oauth_id):
    """Update OAuth credentials"""
    try:
        oauth_creds = OAuthCredential.query.get_or_404(oauth_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'google_client_id' in data:
            oauth_creds.google_client_id = data['google_client_id']
        if 'google_client_secret' in data:
            oauth_creds.google_client_secret = data['google_client_secret']  # In production, encrypt this
        if 'scopes' in data:
            oauth_creds.scopes = data['scopes']
        if 'is_valid' in data:
            oauth_creds.is_valid = data['is_valid']
        
        oauth_creds.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': oauth_creds.to_dict(),
            'message': 'OAuth credentials updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/oauth/<oauth_id>', methods=['DELETE'])
def delete_oauth_credentials(oauth_id):
    """Delete OAuth credentials (mark as invalid)"""
    try:
        oauth_creds = OAuthCredential.query.get_or_404(oauth_id)
        oauth_creds.is_valid = False
        oauth_creds.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'OAuth credentials deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/oauth/<oauth_id>/authorize', methods=['POST'])
def authorize_oauth(oauth_id):
    """Initiate OAuth authorization flow"""
    try:
        oauth_creds = OAuthCredential.query.get_or_404(oauth_id)
        
        # This endpoint would typically redirect to Google's OAuth URL
        # For now, we'll return the authorization URL that the frontend can use
        
        from urllib.parse import urlencode
        
        # Google OAuth 2.0 authorization endpoint
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        
        # OAuth parameters
        params = {
            'client_id': oauth_creds.google_client_id,
            'redirect_uri': request.host_url + 'api/oauth/callback',  # This would be your callback URL
            'scope': oauth_creds.scopes.replace(',', ' ') if oauth_creds.scopes else 'https://www.googleapis.com/auth/calendar',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': oauth_id  # Pass the OAuth credential ID as state
        }
        
        authorization_url = f"{auth_url}?{urlencode(params)}"
        
        return jsonify({
            'success': True,
            'data': {
                'authorization_url': authorization_url,
                'oauth_id': oauth_id
            },
            'message': 'Authorization URL generated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@client_bp.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        # Get authorization code and state from query parameters
        auth_code = request.args.get('code')
        state = request.args.get('state')  # This should be the oauth_id
        error = request.args.get('error')
        
        if error:
            return jsonify({
                'success': False,
                'error': f'OAuth authorization failed: {error}'
            }), 400
        
        if not auth_code or not state:
            return jsonify({
                'success': False,
                'error': 'Missing authorization code or state parameter'
            }), 400
        
        # Get OAuth credentials using the state (oauth_id)
        oauth_creds = OAuthCredential.query.get(state)
        if not oauth_creds:
            return jsonify({
                'success': False,
                'error': 'Invalid OAuth credentials reference'
            }), 404
        
        # Exchange authorization code for access token
        import requests
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': oauth_creds.google_client_id,
            'client_secret': oauth_creds.google_client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': request.host_url + 'api/oauth/callback'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if token_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Token exchange failed: {token_json.get("error_description", "Unknown error")}'
            }), 400
        
        # Update OAuth credentials with tokens
        oauth_creds.access_token = token_json.get('access_token')
        oauth_creds.refresh_token = token_json.get('refresh_token')
        
        # Calculate token expiration
        if 'expires_in' in token_json:
            from datetime import timedelta
            oauth_creds.token_expires_at = datetime.utcnow() + timedelta(seconds=int(token_json['expires_in']))
        
        oauth_creds.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Return a simple HTML page that closes the popup and notifies the parent
        return '''
        <html>
        <head><title>OAuth Success</title></head>
        <body>
            <h2>Authorization Successful!</h2>
            <p>You can close this window now.</p>
            <script>
                // Notify parent window and close popup
                if (window.opener) {
                    window.opener.postMessage({type: 'oauth_success'}, '*');
                }
                setTimeout(() => window.close(), 2000);
            </script>
        </body>
        </html>
        '''
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@client_bp.route('/oauth/<oauth_id>/refresh', methods=['POST'])
def refresh_oauth_token(oauth_id):
    """Refresh OAuth access token using refresh token"""
    try:
        oauth_creds = OAuthCredential.query.get_or_404(oauth_id)
        
        if not oauth_creds.refresh_token:
            return jsonify({
                'success': False,
                'error': 'No refresh token available'
            }), 400
        
        import requests
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'client_id': oauth_creds.google_client_id,
            'client_secret': oauth_creds.google_client_secret,
            'refresh_token': oauth_creds.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if token_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'Token refresh failed: {token_json.get("error_description", "Unknown error")}'
            }), 400
        
        # Update access token
        oauth_creds.access_token = token_json.get('access_token')
        
        # Update refresh token if a new one is provided
        if 'refresh_token' in token_json:
            oauth_creds.refresh_token = token_json['refresh_token']
        
        # Calculate new token expiration
        if 'expires_in' in token_json:
            from datetime import timedelta
            oauth_creds.token_expires_at = datetime.utcnow() + timedelta(seconds=int(token_json['expires_in']))
        
        oauth_creds.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': oauth_creds.to_dict(),
            'message': 'Token refreshed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

