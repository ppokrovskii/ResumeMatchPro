# Resume Match Pro Frontend

Welcome to the frontend repository for Resume Match Pro, a web application designed to help users tailor their CVs to specific job descriptions, ensuring a higher match rate with potential employers.

## Project Overview

Resume Match Pro's frontend is built using React 18 with TypeScript, providing a robust, type-safe, and modern user interface. This application interacts with our backend services to manage file uploads, retrieve files, and get matching results for user CVs against job descriptions.

## Architecture

### Main Components

- **Pages**: Each page corresponds to a route in the application:
  - **HomePage**: Dashboard where users can upload and manage their CVs and job descriptions.
  - **AboutPage**: Provides information about the application and its features.
  - **UserProfilePage**: Allows users to view and edit their profile details.
  - **ResumeAnalysisPage**: Displays suggestions for tailoring CVs based on job descriptions.

- **Components**: Reusable UI components including buttons, input fields, modals, etc.

- **Hooks**: Custom React hooks for managing state and interactions with the backend APIs.

- **Context**: Utilized for global state management across the application, particularly for user authentication.

- **Services**: Abstract the HTTP requests to the backend. Includes:
  - **fileService**: Handles uploading and fetching files.
  - **resultService**: Retrieves analysis results after CVs are matched against job descriptions.

### Integration with Backend

The frontend interacts with the backend through three main API endpoints:
- **GET /files**: Retrieve files that have been uploaded by the user.
- **POST /files**: Allows users to upload CVs and job descriptions.
- **GET /results**: Get matching results after the analysis of CVs against job descriptions.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourrepository/resume-match-pro-frontend.git
   ```

2. **Navigate to the project directory**:
    ```bash
    cd resume-match-pro-frontend
    ```

3. **Install dependencies**:
    ```bash
    npm install
    ```

4. **Start the development server**:
    ```bash
    npm start
    ```

5. **Open your browser** and navigate to `http://localhost:3000` to see the application running.

## Environment Variables

The application uses the following environment variables:

- `REACT_APP_BASE_URL`: Base URL for the application (e.g., http://localhost:3000 for development)
- `REACT_APP_API_URL`: Base URL for the API (e.g., http://localhost:7071/api for development)
- `REACT_APP_B2C_TENANT`: Azure B2C tenant name
- `REACT_APP_B2C_CLIENT_ID`: Azure B2C client ID
- `REACT_APP_B2C_AUTHORITY_DOMAIN`: Azure B2C authority domain

You can create a `.env` file in the root directory with these variables:

```env
REACT_APP_BASE_URL=http://localhost:3000
REACT_APP_API_URL=http://localhost:7071/api
REACT_APP_B2C_TENANT=your_tenant_name
REACT_APP_B2C_CLIENT_ID=your_client_id
REACT_APP_B2C_AUTHORITY_DOMAIN=your_authority_domain
```

For production, these variables should be set in your deployment environment.
