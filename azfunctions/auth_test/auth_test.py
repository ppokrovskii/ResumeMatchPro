import logging
import azure.functions as func
import json
import base64

# create blueprint
auth_test_bp = func.Blueprint()

@auth_test_bp.route(route="auth_test", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def auth_test(req: func.HttpRequest) -> func.HttpResponse:
    """Test endpoint to verify Azure AD B2C authentication.
    Returns user claims if authenticated."""
    
    user_claims = {}
    
    # Get the Authorization header
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return func.HttpResponse(
            "Unauthorized - No Authorization header",
            status_code=401
        )
    
    # X-MS-CLIENT-PRINCIPAL-NAME contains the user's email from B2C
    client_principal_name = req.headers.get('X-MS-CLIENT-PRINCIPAL-NAME')
    if client_principal_name:
        user_claims['email'] = client_principal_name
    
    # X-MS-CLIENT-PRINCIPAL-ID contains the user's object ID from B2C
    client_principal_id = req.headers.get('X-MS-CLIENT-PRINCIPAL-ID')
    if client_principal_id:
        user_claims['id'] = client_principal_id
        
    # X-MS-CLIENT-PRINCIPAL contains all B2C claims in base64 encoded JSON
    client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
    if client_principal:
        try:
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            
            # Extract relevant B2C claims
            user_claims['claims'] = {
                'displayName': next((claim['val'] for claim in claims['claims'] if claim['typ'] == 'name'), None),
                'email': next((claim['val'] for claim in claims['claims'] if claim['typ'] == 'emails'), None),
                'identityProvider': next((claim['val'] for claim in claims['claims'] if claim['typ'] == 'idp'), None),
                'userId': next((claim['val'] for claim in claims['claims'] if claim['typ'] == 'sub'), None),
                'tenantId': next((claim['val'] for claim in claims['claims'] if claim['typ'] == 'tid'), None),
                # Add any other B2C claims you need
            }
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            user_claims['claims_error'] = str(e)
    
    return func.HttpResponse(
        json.dumps(user_claims),
        mimetype="application/json",
        status_code=200
    ) 