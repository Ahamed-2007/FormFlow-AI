"""Python port of config.php — app-wide configuration and error handling."""

import os
import secrets

# Mirrors: session_start() in PHP. Flask handles sessions via a signed
# cookie, so a SECRET_KEY takes the place of PHP's session mechanism.
SECRET_KEY = os.environ.get("FORMFLOW_SECRET_KEY", secrets.token_hex(32))

ERROR_PAGE_HTML = (
    '<!doctype html><html lang="en"><head><meta charset="UTF-8">'
    "<title>FormFlow AI Error</title></head><body>"
    '<main style="max-width:680px;margin:4rem auto;font-family:Arial,sans-serif">'
    "<h1>FormFlow AI could not complete that request</h1>"
    "<p>Please return to the home page and try again.</p>"
    '<p><a href="/">Back to FormFlow AI</a></p></main></body></html>'
)
