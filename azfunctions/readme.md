# Azure Functions

## Local Development Setup

### Prerequisites
- Python 3.11
- Node.js and npm
- Azure Functions Core Tools
- Azurite (Azure Storage Emulator)

### Installation Steps

1. Install Azure Functions Core Tools (choose one method):

   **Option 1 - npm (recommended):**
   ```bash
   npm i -g azure-functions-core-tools@4 --unsafe-perm true
   ```

   **Option 2 - Direct download:**
   Download and install from: https://go.microsoft.com/fwlink/?linkid=2174087

2. Install Azurite (Azure Storage Emulator):
```powershell
npm install -g azurite
```

### Configuration

1. Configure `local.settings.json` with your Azure service credentials:
```json
{
    "IsEncrypted": false,
    "Values": {
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "AZURE_OPENAI_API_KEY": "<your-openai-key>",
        "AZURE_DOCUMENT_INTELLIGENCE_KEY": "<your-doc-intelligence-key>",
        "AZURE_OPENAI_ENDPOINT": "<your-openai-endpoint>",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "<your-deployment-name>",
        "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": "<your-doc-intelligence-endpoint>",
        "MAIN_FRONTEND_URLS": "http://localhost:3000",
        "LANDING_FRONTEND_URLS": "http://localhost:3001"
    },
    "Host": {
        "LocalHttpPort": 7071,
        "CORS": "*",
        "CORSCredentials": true
    }
}
```

### Running Locally

1. Start Azurite in a separate terminal:
```powershell
azurite
```

2. In your main terminal, navigate to the azfunctions directory:
```powershell
cd azfunctions
```

3. Start the Functions host:
```powershell
func start
```

### Accessing the Functions
- Local endpoint: `http://localhost:7071`
- API routes: `http://localhost:7071/api/{route}`
- Available routes:
  - `POST /api/files/upload`: Upload files
  - `GET /api/files`: Get user files
  - `POST /api/matching`: Match resume
  - `GET /api/matching/results`: Get matching results
  - `GET /api/auth_test`: Test authentication

## Cosmos DB Emulator
To install it: https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-develop-emulator?tabs=windows%2Ccsharp&pivots=api-nosql
Navigate to https://localhost:8081/_explorer/index.html to access the data explorer.

# Architecture

### 1. **File Upload Function**

- **Trigger**: HTTP Trigger
- **Functionality**: Handles the uploading of CVs and JDs by users.
- **Azure Services Used**:
  - **Azure Blob Storage**: Stores the uploaded files.
  - **Azure Queue Storage**: Sends a message with file metadata to a queue (`processing-queue`) for further processing.

### 2. **File Processing Function**

- **Trigger**: Azure Queue Trigger (`processing-queue`)
- **Functionality**: Picks up messages from the `processing-queue`, determines the file type, and extracts text from the files. Stores the extracted text in a database.
- **Azure Services Used**:
  - **Azure Blob Storage**: Retrieves files for processing.
  - **Azure Cognitive Services (Document Intelligence Service)**: Extracts text from PDF files.
  - **Custom Logic or Azure Cognitive Service**: Extracts text from DOCX files.
  - **Azure Cosmos DB**: Stores the extracted text associated with user and file metadata.

### 3. **Text Matching Function**

- **Trigger**: Azure Queue Trigger (`matching-queue`)
- **Functionality**: Retrieves text from Azure Cosmos DB and uses Azure OpenAI Service to match CVs against JDs.
- **Azure Services Used**:
  - **Azure Cosmos DB**: Retrieves CV and JD text.
  - **Azure OpenAI Service**: Performs text matching analysis.
  - **Azure Cosmos DB**: Stores matching results.

### 4. **User Files Function**

- **Trigger**: HTTP Trigger
- **Functionality**: Provides a list of files or documents associated with a specific user. It queries the database using the user's identity to retrieve metadata about the files they have access to or have uploaded.
- **Azure Services Used**:
  - **Azure Easy Auth**: Authenticates the user.
  - **Azure Cosmos DB**: Queries for files associated with the authenticated user.

### 5. **Matching Results Function**

- **Trigger**: HTTP Trigger
- **Functionality**: Provides a list of matching results filtered by selected file and sorted by descending matching score. It queries the database using the user's identity to retrieve matching results
- **Azure Services Used**: 
- **Azure Easy Auth**: Authenticates the user.
- **Azure Cosmos DB**: Queries for matching results associated with the authenticated user filtered by selected file.

### 6. **Authentication and Authorization**

- Integrated across applicable functions using **Azure Easy Auth** to secure API endpoints and ensure that users can only access their data.

### Additional Azure Services for Infrastructure and Security

- **Azure Queue Storage**: Used for decoupling the file upload and processing stages, ensuring reliable message delivery and scalable processing.
- **Azure App Service**: Hosts the Azure Functions, providing a scalable and managed hosting environment.
- **Azure Active Directory (AAD)**: Optionally used with Azure Easy Auth for secure authentication, especially if integrating with corporate credentials.

This architecture leverages Azure's serverless and cognitive services to create a scalable, secure, and efficient system for processing and analyzing CVs and JDs. Each component is designed to perform a specific role within the application, ensuring clarity of purpose, ease of maintenance, and the ability to scale components independently based on demand.