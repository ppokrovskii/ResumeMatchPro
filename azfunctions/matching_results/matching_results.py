import logging
from azure import functions as func

from matching_results.models import MatchingResultsRequest, MatchingResultsResponse
from shared.db_service import get_cosmos_db_client
from shared.matching_results_repository import MatchingResultsRepository

matching_results_bp = func.Blueprint("matching_results", __name__)

@matching_results_bp.route(route="results", methods=["GET"])
def get_matching_results(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_matching_results function processed a request.')
    request = MatchingResultsRequest(**req.params)
    cosmos_db_client = get_cosmos_db_client()
    matching_results_repository = MatchingResultsRepository(cosmos_db_client)
    results_from_db = matching_results_repository.get_results_by_file_type_and_id(request.user_id, request.file_id, request.file_type)
    response = MatchingResultsResponse.from_json(results_from_db)
    return func.HttpResponse(response.model_dump_json(), mimetype="application/json")