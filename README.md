# FormFlow AI (Python + HTML/CSS version)

This is a straight code-language conversion of the original PHP project.
No feature, wording, rule, or design was changed — only the implementation
language moved from PHP to Python (Flask + Jinja2 templates) with the same
HTML structure and the exact same CSS file.

## What maps to what

| Original (PHP)                     | Converted (Python)                        |
|-------------------------------------|--------------------------------------------|
| `index.php`                         | `app.py` → `index()` route + `templates/index.html` |
| `analyze.php`                       | `app.py` → `analyze()` route + `templates/analyze.html` |
| `config.php`                        | `config.py` |
| `includes/services.php`             | `formflow/services.py` |
| `includes/banks.php`                | `formflow/banks.py` |
| `includes/translations.php`         | `formflow/translations.py` |
| `includes/official.php`             | `formflow/official.py` |
| `includes/documents.php`            | `formflow/documents.py` |
| `includes/ollama.php`               | `formflow/ollama_client.py` |
| (helper functions inside analyze.php) | `formflow/logic.py` |
| `css/style.css`                     | `static/css/style.css` (byte-for-byte copy) |
| PHP `$_SESSION['formflow']`         | Flask `session['formflow']` (signed cookie session) |

Behavior kept identical:
- Same 4 languages (English/Tamil/Hindi/Malayalam), same translation text.
- Same services, checklist logic, readiness scoring, and journey stages.
- Same Bank KYC bank directory and validation rules.
- Same prompt sent to the local Ollama model (`llama3.2:3b` at
  `http://127.0.0.1:11434`), same follow-up vs. first-run instructions,
  same fallback answers if Ollama is unreachable on a follow-up question.
- Same Word/PDF guide downloads, including the exact same hand-rolled
  minimal PDF writer used as a fallback when no headless Chrome/Edge is
  available (the primary path still tries a headless browser first, same
  as the PHP version did on Windows).
- Same URLs' query parameters (`?mode=`, `?language=`, `?reset=1`,
  `?download=word|pdf`) — only the file extension in the base path
  changed, since Python route paths don't use `.php`
  (`index.php` → `/`, `analyze.php` → `/analyze`).

## Running it

```bash
pip install -r requirements.txt
python app.py
```

The app expects a local [Ollama](https://ollama.com) server running with
the `llama3.2:3b` model pulled (`ollama pull llama3.2:3b`), exactly like
the original PHP app did — nothing about the AI backend changed.

Open http://127.0.0.1:5000/ in your browser.
