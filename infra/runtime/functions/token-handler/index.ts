import { AzureFunction, Context, HttpRequest } from "@azure/functions";

interface B2CRequest {
    step: string;
    client_id: string;
    ui_locales: string;
    email?: string;
    objectId?: string;
    givenName?: string;
    surname?: string;
    displayName?: string;
}

const httpTrigger: AzureFunction = async function (context: Context, req: HttpRequest): Promise<void> {
    context.log('Token handler function processing a request.');

    try {
        const body: B2CRequest = req.body;
        context.log('Request body:', body);

        // Ensure we're handling the token claims step
        if (body.step !== "token-claims") {
            context.res = {
                status: 400,
                body: {
                    version: "1.0.0",
                    status: 400,
                    userMessage: "Invalid step. This endpoint only handles token claims."
                }
            };
            return;
        }

        // Add or modify claims as needed
        const response = {
            version: "1.0.0",
            action: "Continue",
            extension_scopes: ["api://resumematchpro-backend-api/Files.ReadWrite"],
            extension_app_id: process.env.BACKEND_CLIENT_ID,
            claims: {
                // Pass through existing claims
                email: body.email,
                given_name: body.givenName,
                family_name: body.surname,
                name: body.displayName,
                oid: body.objectId,
                // Add any additional claims needed
                scp: "Files.ReadWrite"
            }
        };

        context.log('Sending response:', response);
        context.res = {
            status: 200,
            body: response
        };
    } catch (error) {
        context.log.error('Error processing request:', error);
        context.res = {
            status: 400,
            body: {
                version: "1.0.0",
                status: 400,
                userMessage: "Error processing the request."
            }
        };
    }
};

export default httpTrigger; 