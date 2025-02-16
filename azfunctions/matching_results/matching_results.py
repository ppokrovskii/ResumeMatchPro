import logging
import json
import base64
from azure import functions as func

from matching_results.models import MatchingResultsRequest, MatchingResultsResponse
from shared.db_service import get_cosmos_db_client
from shared.matching_results_repository import MatchingResultsRepository

matching_results_bp = func.Blueprint("matching_results", __name__)

@matching_results_bp.route(route="results", methods=["GET"])
def get_matching_results(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_matching_results function processed a request.')
    try:
        # Get user_id from B2C claims
        client_principal = req.headers.get('X-MS-CLIENT-PRINCIPAL')
        if not client_principal:
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Missing user claims"}),
                mimetype="application/json",
                status_code=401
            )

        try:
            claims_json = base64.b64decode(client_principal).decode('utf-8')
            claims = json.loads(claims_json)
            user_id = next((claim['val'] for claim in claims['claims'] 
                        if claim['typ'] == 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier'), None)
            
            if not user_id:
                return func.HttpResponse(
                    body=json.dumps({"error": "Unauthorized - Missing user ID in claims"}),
                    mimetype="application/json",
                    status_code=401
                )
        except Exception as e:
            logging.error(f"Error decoding claims: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({"error": "Unauthorized - Invalid claims format"}),
                mimetype="application/json",
                status_code=401
            )

        # Get file_id and file_type from request parameters
        request = MatchingResultsRequest(
            file_id=req.params.get('file_id'),
            file_type=req.params.get('file_type')
        )

        cosmos_db_client = get_cosmos_db_client()
        matching_results_repository = MatchingResultsRepository(cosmos_db_client)
        results_from_db = matching_results_repository.get_results_by_file_type_and_id(
            user_id, 
            request.file_id, 
            request.file_type
        )
        response = MatchingResultsResponse.from_json(results_from_db)
        return func.HttpResponse(response.model_dump_json(), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error getting matching results: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({"error": "Internal Server Error"}),
            mimetype="application/json",
            status_code=500
        )