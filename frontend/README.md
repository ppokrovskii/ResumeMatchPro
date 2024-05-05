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
