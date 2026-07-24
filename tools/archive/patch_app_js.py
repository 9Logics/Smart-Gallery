import re

with open('static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r"emptyTrashBtn:\s*document\.getElementById\('empty-trash-btn'\),\s*", '', content)
content = re.sub(r"elements\.emptyTrashBtn\.addEventListener\('click',\s*emptyRecycleBin\);\s*", '', content)
content = re.sub(r"elements\.emptyTrashBtn\.classList\.add\('hidden'\);\s*", '', content)
content = re.sub(r"elements\.emptyTrashBtn\.classList\.remove\('hidden'\);\s*", '', content)

func_pattern = re.compile(r"function emptyRecycleBin\(\)\s*\{.*?\}(?=\n\nfunction restoreAllRecycleBin)", re.DOTALL)
content = func_pattern.sub('', content)

# Also update the purgeItem confirm message
old_confirm = 'Are you sure you want to permanently delete this file?'
new_confirm = 'Are you sure you want to move this file to the Windows Recycle Bin?'
content = content.replace(old_confirm, new_confirm)

old_success = 'File permanently deleted!'
new_success = 'File moved to Recycle Bin!'
content = content.replace(old_success, new_success)

# Fix multi selection purge message
old_multi_confirm = 'Are you sure you want to permanently delete'
new_multi_confirm = 'Are you sure you want to move to the Recycle Bin'
content = content.replace(old_multi_confirm, new_multi_confirm)

with open('static/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('app.js updated successfully.')
