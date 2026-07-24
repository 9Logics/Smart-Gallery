# Project Rules

1. **Auto-Kill Python Server**: Whenever the user asks you to make backend changes to the application (like editing `app.py`), you must always proactively kill the running Python server using `taskkill /F /IM python.exe` (on Windows) to suspend the app. This ensures nothing breaks and the user is forced to restart the server to load the new backend changes.
