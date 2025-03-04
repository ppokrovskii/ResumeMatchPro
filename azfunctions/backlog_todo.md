this file contains list of to do items, each of them can be defect, story or refactoring. once an item is done it has to be moved to backlog_done.md file. after each task completion commit and push to develop, then watch github actions until succesful completion.

## User Stories

### Fix global drag-and-drop functionality
- **Priority**: High
- **Description**: As a user, I want to be able to drag and drop multiple files to any part of the application, with the entire browser window becoming a drop area. When I drag files over the browser, the whole page should show an overlay with text like "drop files anywhere to upload and process them". Currently, the drag-and-drop functionality doesn't work as expected.
- **Acceptance Criteria**:
  - When dragging files over any part of the application, a full-page overlay should appear
  - The overlay should have clear instructions about dropping files
  - Users should be able to drop files anywhere on the screen
  - The application should properly handle the file upload process after dropping
  - The component should be integrated at the App level instead of just the HomePage 