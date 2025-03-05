this file contains list of to do items, each of them can be defect, story or refactoring. once an item is done it has to be moved to backlog_done.md file. after each task completion commit and push to develop, then watch github actions until succesful completion.



defect: when I upload a file request fails with error '"Invalid request: 1 validation error for FileUploadRequest\ntype\n  Input should be 'CV' or 'JD' [type=enum, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.7/v/enum"' Type should not be required as it is determined by AI during file processing.

story: when I drag and drop a file I should not be asked to click Ok fo CV and Cancel for JD. this question is redundant as type is determined by AI during file processing. 

story: as a user I want to be able to see progress of files processing.

defect: when I select a CV and a Job Description at the same time and then click on close button (with cross icon) on any of them then both closes while only one should get closed.