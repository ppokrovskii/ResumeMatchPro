this file contains list of to do items, each of them can be defect, story or refactoring. once an item is done it has to be moved to backlog_done.md file. after each task completion commit and push to develop, then watch github actions until succesful completion.

Test: why our uat tests were not catching issue when file_processing function was sending file_id while match_resume function was expecting id argument? can you adjust uat test so it catches such things?

Defect: on CV details form Close button must be at the top right corner on the same line with 'CVs' header

Story: do not show file status on each file and do not return it in GET /api/files endpoint. when I upload a file or set of files I want to see a message in place of HomePage_globalUploadMessage saying like 'Files processing: 11/15 Files matching: 2/35'. If any files processing is in progress this message text should get updated every second.

Story: in https://resumematchpro-dev-function-app.azurewebsites.net/api/files return nullable Name and Job Title. if Name is coming in response then frontend should show {Name} - {Job Title} instead of file name. For JDs it should be only {Job Title}
