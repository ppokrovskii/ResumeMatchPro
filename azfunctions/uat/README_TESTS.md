# UAT (User Acceptance Testing) for ResumeMatchPro

This directory contains end-to-end tests that verify the functionality of the ResumeMatchPro application using real cloud services through local emulators.

## Prerequisites

1. Make sure you have Azure local emulators running:
   - Azure Storage Emulator (or Azurite) for Blob and Queue storage
   - Cosmos DB Emulator

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up the environment variables:
   - Copy `.env.test` from the `tests` directory to this directory
   - Update the values as needed for your local environment

## Available Tests

### File Processing Test

Tests the file processing functionality by uploading a JD file, processing it, and verifying the results.

```
python -m pytest test_file_processing_e2e.py::test_file_processing_e2e -v
```

### Complete E2E Flow with Matching

Tests the complete flow:
1. Uploads a JD file
2. Uploads a CV file
3. Verifies both files are processed
4. Verifies matching is performed and results are available

```
python -m pytest test_file_processing_e2e.py::test_complete_e2e_flow_with_matching -v
```

### Running from the Script

For convenience, you can use the provided script:

#### Windows
```
run_complete_e2e_test.bat
```

#### Linux/Mac
```
python run_complete_e2e_test.py
```

By default, the test assumes the local function app is running at `http://localhost:7071/api`. 
You can specify a different endpoint with the `--function-url` parameter:

```
python run_complete_e2e_test.py --function-url https://resumematchpro-dev-function-app.azurewebsites.net/api
```

## Troubleshooting

1. If the tests fail with connection errors, make sure the local emulators are running.
2. If authentication errors occur, verify your environment variables are set correctly.
3. For timeout errors, you may need to increase the `max_wait_time` in the test scripts.
4. Check the logs for detailed information about what's happening during the test.

## Test Data

The test uses the following files:
- `test_data/JD - iOS_Junior.docx`: A sample job description
- `test_data/Pavel_Pokrovskii_-_Head_of_Engineering.pdf`: A sample CV/resume

You can add more test files to the `test_data` directory as needed. 