this file contains list of completed items

story: Remove upload areas from CVs and Job Descriptions sections. Add a message on top of both sections with upload button instead saying 'Upload or Drag and Drop a CV or Job Description anywhere on the screen'

story: when I drag and drop a file I should not be asked to click Ok fo CV and Cancel for JD. this question is redundant as type is determined by AI during file processing. 

defect: when I upload a file request fails with error '"Invalid request: 1 validation error for FileUploadRequest\ntype\n  Input should be 'CV' or 'JD' [type=enum, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.7/v/enum"' Type should not be required as it is determined by AI during file processing.

defect: while list of files is loading CVs and Job Descriptions sections look ugly, 'Loading Files' message and spinner are not fully visible, and some weird scroll is shown on the side of each section

defect: when I select a CV and a Job Description at the same time and then click on close button (with cross icon) on any of them then both closes while only one should get closed.

defect: request like below: curl 'https://resumematchpro-dev-function-app.azurewebsites.net/api/files' \
  -H 'Accept: application/json' \
  -H 'Accept-Language: en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,ar;q=0.6' \
  -H 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6Ilg1ZVhrNHh5b2pORnVtMWtsMll0djhkbE5QNC1jNTdkTzZRR1RWQndhTmsiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiI1MGIyMWMwZi1mNTA1LTRkMzAtOTdmOS0wMzNiNTJlOTQyNWMiLCJpc3MiOiJodHRwczovL3Jlc3VtZW1hdGNocHJvZGV2LmIyY2xvZ2luLmNvbS80YmFiNDMxMi02NzZjLTQyY2ItYWM5Zi00OTMxZjA0MzhkNmUvdjIuMC8iLCJleHAiOjE3NDExOTg0MjIsIm5iZiI6MTc0MTE5NDgyMiwib2lkIjoiZTYxMTRjNjktZWM3ZC00ODZlLTk0MDEtYmU4ZWU0OTg5MjlmIiwic3ViIjoiZTYxMTRjNjktZWM3ZC00ODZlLTk0MDEtYmU4ZWU0OTg5MjlmIiwibmFtZSI6IlBhdmVsIFBva3JvdnNraWkiLCJlbWFpbHMiOlsicHBva3JvdnNraXkrdGVzdEBnbWFpbC5jb20iXSwidGZwIjoiQjJDXzFfc2lnbnVwc2lnbmluIiwibm9uY2UiOiIwMTk1NjcxYi04NDY3LTc2ZDctODg5ZS0wNjk3ZGVkZjc5ZDciLCJzY3AiOiJGaWxlcy5SZWFkV3JpdGUiLCJhenAiOiI0MjUxN2FiNi1lMTI0LTQxM2ItOGUxZi1iYTRkMzhlMTNjOWMiLCJ2ZXIiOiIxLjAiLCJpYXQiOjE3NDExOTQ4MjJ9.hiywKWjIRgKcpYEKepzQdcOrTJuUh6rCu6WOKfy8t9QB3200dpiAYLocssquFrlZWbZnBmg6fDdtY7beuqbRYUQ5P2XHED_YX9PjwNoO8qDAjXxLxeLxAmuxL1ScfWx_yW4UcTQvBKNHk0PV3B0bav5Y6LnIu1jTsAUT9aQd9xIbsA4gGLBAjGl4E6Mzi7M3EeOZUVwle9JoIC8D7wOa-NS1wS0QKlOeqcVV40i18_7KZNihqIlmQYRpamVT9kmk8ZQ19oFru4vjgRnugWQpwx8Zj2h64RP3qXjI6loZkSNmBUkl1Q4DPcey9JIfATTRnVqM5u0iyPHNBWf_rtIOow' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://app.dev.resumematch.pro' \
  -H 'Referer: https://app.dev.resumematch.pro/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: cross-site' \
  -H 'Sec-Fetch-Storage-Access: active' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'sec-ch-ua: "Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"'

returns: {
    "error": "2 validation errors for UserFilesResponse\nfiles.11.type\n  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.7/v/string_type\nfiles.12.type\n  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]\n    For further information visit https://errors.pydantic.dev/2.7/v/string_type"
}

Fix: Made the 'type' field in the File model optional to handle null values.
