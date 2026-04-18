# get-confluence-pages
Atlassin Confluence pages download / backup script in Python

This script uses https://github.com/atlassian-api/atlassian-python-api to:
1. Load credentials from credentials.txt
2. Load a list of parent page IDs from pages.txt
3. Download and save all pages and subpages of the IDs in PDF.
* directories are created for each parent page ID
* already downloaded pages are skipped

It is advised to set up a virtual Python env in your home, install atlassian-python-api into that and use that for this script.
Currently the script is configured to download from Cloud confluence instances.

Caveats: you will need to edit one file in your virtual environment as descsribed in: https://github.com/atlassian-api/atlassian-python-api/issues/1636
It appears the new Confluence updated in March forces use of the v2 API, that atlassian-python-api is not currently doing.
