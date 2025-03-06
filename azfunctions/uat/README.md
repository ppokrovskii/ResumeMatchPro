# User Acceptance Testing (UAT)

This directory contains User Acceptance Tests (UAT) for the ResumeMatchPro Azure Functions. These tests are designed to run end-to-end tests that verify the functionality of the system with real Azure service emulators.

## Prerequisites

Before running the UAT tests, you need to ensure that the following emulators are running:

1. **Azure Cosmos DB Emulator**: Required for database operations
2. **Azurite**: Required for Blob Storage and Queue operations

## Running the Tests

You can run the UAT tests using the provided `run_uat_tests.py` script:

```bash
# Run all UAT tests
python azfunctions/uat/run_uat_tests.py

# Run a specific UAT test
python azfunctions/uat/run_uat_tests.py --test-file test_file_processing_e2e.py
```

Alternatively, you can run the tests directly using pytest:

```bash
# From the azfunctions directory
cd azfunctions
python -m pytest uat -v
```

## Available Tests

### File Processing E2E Test

The `test_file_processing_e2e.py` file contains an end-to-end test for the file processing functionality. This test:

1. Takes a sample document (`.data\Onboarding\Job Description\iOS Developer\JD - iOS_Junior.docx`)
2. Uploads it to Azure Blob Storage emulator
3. Creates a file record in Cosmos DB emulator
4. Processes the file using the Azure Functions
5. Verifies the file was processed correctly
6. Cleans up created resources

## Troubleshooting

If the tests fail, check the following:

1. Make sure all emulators are running (Cosmos DB Emulator, Azurite)
2. Check that the `.env.test` file in the `azfunctions/tests` directory is correctly configured
3. Verify that the test file path is correct (`.data\Onboarding\Job Description\iOS Developer\JD - iOS_Junior.docx`)
4. Review the log output for specific error messages

## Adding New UAT Tests

To add a new UAT test:

1. Create a new test file in the `uat` directory
2. Follow the pattern in existing tests to set up the test environment
3. Use real Azure service emulators for testing
4. Make sure to include cleanup code to remove any resources created during the test 