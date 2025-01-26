import logging
import json
import azure.functions as func
from azure.functions import HttpRequest, HttpResponse

from shared.db_service import get_cosmos_db_client
from shared.user_repository import UserRepository
from users.models import CreateUserRequest, CreateUserResponse, UserDb, UpdateUserLimitsRequest
from datetime import datetime

# create blueprint
users_bp = func.Blueprint()

@users_bp.route(route="users", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
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
        response = CreateUserResponse(**saved_user.model_dump())
        
        return func.HttpResponse(
            body=response.model_dump_json(),
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

def update_user_limits(req: HttpRequest) -> HttpResponse:
    try:
        # Check if user is admin from access token claims
        auth_header = req.headers.get('Authorization', '')
        if not auth_header:
            return HttpResponse(
                body=json.dumps({"error": "Unauthorized - No token provided"}),
                mimetype="application/json",
                status_code=401
            )

        # Get the claims from the X-MS-CLIENT-PRINCIPAL-CLAIMS header
        claims_header = req.headers.get('X-MS-CLIENT-PRINCIPAL-CLAIMS', '')
        if not claims_header:
            return HttpResponse(
                body=json.dumps({"error": "Unauthorized - No claims found"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims = json.loads(claims_header)
            is_admin = any(claim.get('typ') == 'extension_IsAdmin' and claim.get('val') == 'true' for claim in claims)
            if not is_admin:
                return HttpResponse(
                    body=json.dumps({"error": "Unauthorized - Admin access required"}),
                    mimetype="application/json",
                    status_code=403
                )
        except json.JSONDecodeError:
            return HttpResponse(
                body=json.dumps({"error": "Unauthorized - Invalid claims"}),
                mimetype="application/json",
                status_code=401
            )

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
        response = CreateUserResponse(
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
            body=json.dumps(response.model_dump(), default=str),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return HttpResponse(
            body=json.dumps({"error": f"Internal server error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )

@users_bp.route(route="users/search", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def search_users(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Check if user is admin from access token claims
        auth_header = req.headers.get('Authorization', '')
        if not auth_header:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - No token provided"}),
                mimetype="application/json",
                status_code=401
            )

        # Get the claims from the X-MS-CLIENT-PRINCIPAL-CLAIMS header
        claims_header = req.headers.get('X-MS-CLIENT-PRINCIPAL-CLAIMS', '')
        if not claims_header:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - No claims found"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims = json.loads(claims_header)
            is_admin = any(claim.get('typ') == 'extension_IsAdmin' and claim.get('val') == 'true' for claim in claims)
            if not is_admin:
                return func.HttpResponse(
                    body=json.dumps({"error": "Unauthorized - Admin access required"}),
                    mimetype="application/json",
                    status_code=403
                )
        except json.JSONDecodeError:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Invalid claims"}),
                mimetype="application/json",
                status_code=401
            )

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
        response = [CreateUserResponse(**user.model_dump()) for user in users]
        
        return func.HttpResponse(
            body=json.dumps([r.model_dump() for r in response], default=str),
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