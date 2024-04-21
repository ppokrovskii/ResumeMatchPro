# cosmos db emulator
### to install it ```https://learn.microsoft.com/en-us/azure/cosmos-db/how-to-develop-emulator?tabs=windows%2Ccsharp&pivots=api-nosql```
### Navigate to ```https://localhost:8081/_explorer/index.html``` to access the data explorer.


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
  - **Azure Cosmos DB** (Optionally): Stores matching results.

### 4. **User Files Function**

- **Trigger**: HTTP Trigger
- **Functionality**: Provides a list of files or documents associated with a specific user. It queries the database using the user's identity to retrieve metadata about the files they have access to or have uploaded.
- **Azure Services Used**:
  - **Azure Easy Auth**: Authenticates the user.
  - **Azure Cosmos DB**: Queries for files associated with the authenticated user.

### 5. **Authentication and Authorization**

- Integrated across applicable functions using **Azure Easy Auth** to secure API endpoints and ensure that users can only access their data.

### Additional Azure Services for Infrastructure and Security

- **Azure Queue Storage**: Used for decoupling the file upload and processing stages, ensuring reliable message delivery and scalable processing.
- **Azure App Service**: Hosts the Azure Functions, providing a scalable and managed hosting environment.
- **Azure Active Directory (AAD)**: Optionally used with Azure Easy Auth for secure authentication, especially if integrating with corporate credentials.

This architecture leverages Azure's serverless and cognitive services to create a scalable, secure, and efficient system for processing and analyzing CVs and JDs. Each component is designed to perform a specific role within the application, ensuring clarity of purpose, ease of maintenance, and the ability to scale components independently based on demand.