import logging
import json
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse
import jwt
from jwt.exceptions import InvalidTokenError
import base64

from shared.db_service import get_cosmos_db_client
from shared.user_repository import UserRepository
from users.models import CreateUserRequest, CreateUserResponse, UserDb, UpdateUserLimitsRequest
from datetime import datetime

# create blueprint
users_bp = func.Blueprint("users", __name__)

def verify_admin_token(req: HttpRequest) -> bool:
    """Verify if the user is an admin from the client principal."""
    try:
        # Get client principal from headers
        client_principal = req.headers.get('x-ms-client-principal')
        if not client_principal:
            logging.warning("No x-ms-client-principal header found")
            return False

        try:
            # Decode and parse the client principal
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            
            # Log claims for debugging
            logging.info(f"Claims received: {claims}")
            
            # Check for admin claim
            is_admin = next((
                claim['val'] for claim in claims['claims']
                if claim['typ'] == 'extension_IsAdmin'
            ), None) == 'true'
            
            logging.info(f"Admin check result: {is_admin}")
            return is_admin
            
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            return False
            
    except Exception as e:
        logging.error(f"Error checking admin status: {str(e)}")
        return False

def require_admin(req: HttpRequest) -> HttpResponse | None:
    """Check if the request is from an admin user.
    Returns None if authorized, HttpResponse with error if not."""
    # Get client principal
    client_principal = req.headers.get('x-ms-client-principal')
    if not client_principal:
        return HttpResponse(
            body=json.dumps({"error": "Unauthorized - No authentication found"}),
            mimetype="application/json",
            status_code=401
        )
    
    if not verify_admin_token(req):
        return HttpResponse(
            body=json.dumps({"error": "Unauthorized - Admin access required"}),
            mimetype="application/json",
            status_code=403
        )
    return None

@users_bp.route(route="users", methods=["POST"])
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing user registration request')
    
    # Check admin authorization
    auth_response = require_admin(req)
    if auth_response:
        return auth_response
    
    try:
        # Parse request body
        req_body = req.get_json()
        create_request = CreateUserRequest(**req_body)
        
        # Get DB client and repository
        cosmos_db_client = get_cosmos_db_client()
        user_repository = UserRepository(cosmos_db_client)
        
        # Check if user already exists
        existing_user = user_repository.get_user(create_request.userId)
        if existing_user:
            return func.HttpResponse(
                body=json.dumps({"error": "User already exists"}),
                mimetype="application/json",
                status_code=409
            )
            
        # Create user DB model
        user_db = UserDb(
            userId=create_request.userId,
            email=create_request.email,
            name=create_request.name,
            isAdmin=create_request.isAdmin,
            filesLimit=create_request.filesLimit,
            matchingLimit=create_request.matchingLimit
        )
        
        # Save to database
        saved_user = user_repository.create_user(user_db.model_dump())
        
        # Convert to response model
        response_data = CreateUserResponse(**saved_user.model_dump())
        
        return func.HttpResponse(
            body=response_data.model_dump_json(),
            mimetype="application/json",
            status_code=201
        )
    except ValueError as e:
        return func.HttpResponse(
            body=json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error"}),
            mimetype="application/json",
            status_code=500
        )

@users_bp.route(route="users/limits", methods=["PUT"])
def update_user_limits(req: HttpRequest) -> HttpResponse:
    # Check admin authorization
    auth_response = require_admin(req)
    if auth_response:
        return auth_response
    
    try:
        # Parse request body
        try:
            req_body = req.get_json()
            update_request = UpdateUserLimitsRequest(**req_body)
        except Exception as e:
            return HttpResponse(
                body=json.dumps({"error": f"Invalid request: {str(e)}"}),
                mimetype="application/json",
                status_code=400
            )

        # Get user from repository
        cosmos_client = get_cosmos_db_client()
        user_repository = UserRepository(cosmos_client)
        user = user_repository.get_user(update_request.userId)
        
        if not user:
            return HttpResponse(
                body=json.dumps({"error": "User not found"}),
                mimetype="application/json",
                status_code=404
            )

        # Update user limits
        user.filesLimit = update_request.filesLimit
        user.matchingLimit = update_request.matchingLimit
        updated_user = user_repository.update_user(user)

        # Return updated user
        response_data = CreateUserResponse(
            userId=updated_user.userId,
            email=updated_user.email,
            name=updated_user.name,
            isAdmin=updated_user.isAdmin,
            filesLimit=updated_user.filesLimit,
            matchingLimit=updated_user.matchingLimit,
            matchingUsedCount=updated_user.matchingUsedCount,
            filesCount=updated_user.filesCount,
            createdAt=updated_user.createdAt
        )

        return HttpResponse(
            body=json.dumps(response_data.model_dump(), default=str),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return HttpResponse(
            body=json.dumps({"error": f"Internal server error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )

@users_bp.route(route="users/search", methods=["GET"])
def search_users(req: func.HttpRequest) -> func.HttpResponse:
    # Debug logging for headers
    auth_header = req.headers.get('Authorization', '')
    client_principal = req.headers.get('x-ms-client-principal', '')
    logging.info(f"Debug headers - Authorization: {auth_header}")
    logging.info(f"Debug headers - x-ms-client-principal: {client_principal}")
    
    # Check admin authorization
    auth_response = require_admin(req)
    if auth_response:
        return auth_response
    
    try:
        # Get search query
        search_query = req.params.get('q', '')
        if not search_query:
            return func.HttpResponse(
                body=json.dumps({"error": "Search query is required"}),
                mimetype="application/json",
                status_code=400
            )

        # Get DB client and repository
        cosmos_db_client = get_cosmos_db_client()
        user_repository = UserRepository(cosmos_db_client)
        
        # Search users
        users = user_repository.search_users(search_query)
        
        if not users:
            return func.HttpResponse(
                body=json.dumps({"error": "No users found"}),
                mimetype="application/json",
                status_code=404
            )
            
        # Convert to response model
        response_data = [CreateUserResponse(**user.model_dump()) for user in users]
        
        return func.HttpResponse(
            body=json.dumps([r.model_dump() for r in response_data], default=str),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error searching users: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": f"Internal server error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )

@users_bp.route(route="users/me", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_current_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing get current user request')
    
    try:
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            logging.error("Missing X-MS-CLIENT-PRINCIPAL header")
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized - Missing user claims"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            user_id = next((claim['val'] for claim in claims['claims'] 
                        if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)
            
            if not user_id:
                logging.error("No user ID found in claims")
                return func.HttpResponse(
                    json.dumps({"error": "Unauthorized - Missing user ID in claims"}),
                    mimetype="application/json",
                    status_code=401
                )
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Unauthorized - Invalid claims format"}),
                mimetype="application/json",
                status_code=401
            )

        # Get user from repository
        cosmos_client = get_cosmos_db_client()
        user_repository = UserRepository(cosmos_client)
        user = user_repository.get_user(user_id)
        
        if not user:
            return func.HttpResponse(
                json.dumps({"error": "User not found"}),
                mimetype="application/json",
                status_code=404
            )

        # Return user details
        response_data = CreateUserResponse(
            userId=user.userId,
            email=user.email,
            name=user.name,
            isAdmin=user.isAdmin,
            filesLimit=user.filesLimit,
            matchingLimit=user.matchingLimit,
            matchingUsedCount=user.matchingUsedCount,
            filesCount=user.filesCount,
            createdAt=user.createdAt
        )

        return func.HttpResponse(
            json.dumps(response_data.model_dump(), default=str),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Error getting current user: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        ) 