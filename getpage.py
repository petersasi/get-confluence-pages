from atlassian import Confluence
import requests
import sys
import os
import re

# If you want to use a session, you can create it like this:
#session =  requests.Session()

# Read password from external file
with open('credentials.txt', 'r') as f:
    conf_password = f.read().strip()

# Insert your organization's URL in place of ORGANIZATION
# and username/email login in place of USER_EMAIL
confluence = Confluence(
    url='https://ORGANIZATION.atlassian.net',
    username='USER_EMAIL',
    password=conf_password,
    cloud=True,
    api_version='cloud')

def sanitize_filename(name: str) -> str:
    """Sanitize the page title to be a valid filename."""
    return re.sub(r'[^\w\s-]', '_', name).strip()

def tree_downloader(confluence: Confluence, parent_id: str, children: list) -> list:
    list_id = []
    list_id.append(parent_id)
    for i in children:
        if isinstance(i, str):
            i_id = i
        else:
            i_id = i['id']
        grandchildren = confluence.get_child_pages(i_id)
        list_id.append(i_id)
        if grandchildren:
            list_id.extend(tree_downloader(confluence, i_id, grandchildren))
    return list_id

# 1. Read PARENT_PAGE_IDs from a file
print("Step: Reading 'pages.txt' for Parent IDs...")
try:
    with open('pages.txt', 'r') as f:
        parent_ids = [line.strip() for line in f if line.strip()]
    print(f"Found {len(parent_ids)} Parent IDs to process.")
except FileNotFoundError:
    print("Error: 'pages.txt' not found.")
    sys.exit(1)

# 2. Iterate through each PARENT_PAGE_ID
for PARENT_PAGE_ID in parent_ids:
    print(f"\n--- Processing Parent ID: {PARENT_PAGE_ID} ---")
    try:
        # Get parent page info
        print(f"Fetching metadata for parent page {PARENT_PAGE_ID}...")
        parent_page = confluence.get_page_by_id(PARENT_PAGE_ID)
        parent_title = parent_page['title']
        
        # Sanitize and create directory
        clean_parent_title = sanitize_filename(parent_title)
        dir_name = f"{clean_parent_title}{PARENT_PAGE_ID}"
        
        if not os.path.exists(dir_name):
            print(f"Action: Creating directory '{dir_name}'")
            os.makedirs(dir_name)
        else:
            print(f"Status: Directory '{dir_name}' already exists.")

        # Fetch all children recursively
        print(f"Mapping page tree for '{parent_title}'...")
        initial_children = confluence.get_child_pages(PARENT_PAGE_ID)
        all_pages = tree_downloader(confluence, PARENT_PAGE_ID, initial_children)
        print(f"Status: Found {len(all_pages)} total pages in this tree.")

        for i in all_pages:
            p = confluence.get_page_by_id(i)
            title = p['title']
            clean_title = sanitize_filename(title)
            id = p['id']
            
            # 3. Define path inside the created directory
            pdf_name = os.path.join(dir_name, f"{clean_title}{id}.pdf")
            
            if os.path.exists(pdf_name):
                print(f"  [Skip] '{clean_title}' (ID: {id}) already exists.")
                continue

            print(f"  [Download] Exporting '{title}' to {pdf_name}...")
            
            try:
                content = confluence.export_page(id)
                with open(pdf_name, 'wb') as file_pdf:
                    file_pdf.write(content)
                print(f"  [Success] Saved {id}.pdf")
            except Exception as e:
                print(f"  [Error] Failed to download page {id}: {e}")
                
    except Exception as e:
        print(f"Critical Error processing Parent ID {PARENT_PAGE_ID}: {e}")

print("\n--- All tasks completed successfully ---")
