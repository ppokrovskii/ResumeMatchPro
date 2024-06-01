import logging
import os
import azure.functions as func
from pydantic import ValidationError

from contact_details.contact_details_repository import ContactDetailsRepository
from contact_details.db_service import get_cosmos_db_client
from contact_details.models import ContactDetailsDbModelCreate
from contact_details.schemas import ContactDetailsCreate, ContactDetailsResponse, ManyContactDetailsResponse


contact_details_bp = func.Blueprint("contact_details", __name__)

@contact_details_bp.route("contact_details", methods=["POST"])
def contact_details(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('contact_details started')
    # validate message
    try:
        contact_details = ContactDetailsCreate(**req.get_json())
    except ValidationError as e:
        # return bad request if validation failed
        return func.HttpResponse(f"Invalid message: {e}", status_code=400)
    # Save file metadata to database
    cosmos_db_client = get_cosmos_db_client()
    contact_details_repository = ContactDetailsRepository(cosmos_db_client)
    try:
        contact_details_db_model = ContactDetailsDbModelCreate(**contact_details.model_dump(mode="json"))  # mode="json"?
        # file_metadata = files_db_service.upsert_file_meta_data(files_container, file_metadata)
        contact_details_db_model = contact_details_repository.upsert_contact_details(
            contact_details_db_model.model_dump(mode="json", exclude_none=True)
            )
    except ValidationError as e:
        logging.error(f"ValidationError: {e}")
        return func.HttpResponse("Internal Server Error!",status_code=500)
    except Exception as e:
        logging.error(f"Exception: {e}")
        return func.HttpResponse("Internal Server Error!",status_code=500)
    # return response
    contact_details_response = ContactDetailsResponse(**contact_details_db_model.model_dump(mode="json", exclude_none=True))
    return func.HttpResponse(contact_details_response.model_dump_json(), status_code=200)


# get all contact details function
@contact_details_bp.route("contact_details", methods=["GET"])
def get_contact_details(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('get_contact_details started')
    # get contact details from database
    cosmos_db_client = get_cosmos_db_client()
    contact_details_repository = ContactDetailsRepository(cosmos_db_client)
    contact_details_db_models = contact_details_repository.get_all_contact_details()
    # return response
    contact_details_responses = [ContactDetailsResponse(**item.model_dump(mode="json", exclude_none=True)) for item in contact_details_db_models]
    many_contact_details_response = ManyContactDetailsResponse(contact_details=contact_details_responses)
    return func.HttpResponse(many_contact_details_response.model_dump_json(exclude_none=True), status_code=200, mimetype="application/json")

