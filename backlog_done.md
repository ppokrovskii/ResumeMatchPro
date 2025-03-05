this file contains list of completed items

story: Remove upload areas from CVs and Job Descriptions sections. Add a message on top of both sections with upload button instead saying 'Upload or Drag and Drop a CV or Job Description anywhere on the screen'

story: when I drag and drop a file I should not be asked to click Ok fo CV and Cancel for JD. this question is redundant as type is determined by AI during file processing. 

defect: when I upload a file request fails with error '"Invalid request: 1 validation error for FileUploadRequest\ntype\n  Input should be 'CV' or 'JD' [type=enum, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.7/v/enum"' Type should not be required as it is determined by AI during file processing.

defect: while list of files is loading CVs and Job Descriptions sections look ugly, 'Loading Files' message and spinner are not fully visible, and some weird scroll is shown on the side of each section

defect: when I select a CV and a Job Description at the same time and then click on close button (with cross icon) on any of them then both closes while only one should get closed.
