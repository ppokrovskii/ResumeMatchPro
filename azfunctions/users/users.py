import logging
import json
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse
import jwt
from jwt.exceptions import InvalidTokenError

from shared.db_service import get_cosmos_db_client
from shared.user_repository import UserRepository
from users.models import CreateUserRequest, CreateUserResponse, UserDb, UpdateUserLimitsRequest
from datetime import datetime

# create blueprint
users_bp = func.Blueprint("users", __name__)

def verify_admin_token(auth_header: str) -> bool:
    """Verify if the user is an admin from the JWT token."""
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    try:
        # Extract token from Bearer header
        token = auth_header.split(' ')[1]
        # Decode token without verification (we trust Azure B2C)
        decoded = jwt.decode(token, options={"verify_signature": False})
        # Check if user is admin
        return decoded.get('extension_IsAdmin') == True
    except (InvalidTokenError, IndexError) as e:
        logging.error(f"Error verifying admin token: {str(e)}")
        return False

def require_admin(func):
    """Decorator to require admin access for endpoints."""
    def wrapper(req: func.HttpRequest) -> func.HttpResponse:
        auth_header = req.headers.get('Authorization', '')
        if not auth_header:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - No token provided"}),
                mimetype="application/json",
                status_code=401
            )
        
        if not verify_admin_token(auth_header):
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Admin access required"}),
                mimetype="application/json",
                status_code=403
            )
            
        return func(req)
    return wrapper


@users_bp.route(name="create_user", route="users", methods=["POST"])
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing user registration request')
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


@users_bp.route(name="update_user_limits", route="users/limits", methods=["PUT"])
def update_user_limits(req: HttpRequest) -> HttpResponse:
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


@users_bp.route(name="search_users", route="users/search", methods=["GET"])
def search_users(req: func.HttpRequest) -> func.HttpResponse:
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