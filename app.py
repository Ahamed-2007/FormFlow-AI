"""FormFlow AI — Python/Flask port of the original PHP application.

This file is the Python equivalent of index.php + analyze.php combined:
one route serves the home/apply/guidelines page, the other runs the
readiness analysis (talks to the local Ollama model) and serves the
result dashboard, including the Word/PDF guide downloads.

Every piece of visible text, every rule, and every step of the original
PHP logic has been kept as-is — only the language changed.
"""

import json
import re

from flask import Flask, Response, redirect, render_template, request, session, url_for

import config
from formflow.banks import formflow_banks, formflow_kyc_purposes
from formflow.documents import build_pdf_document, build_word_document, formflow_guide_data
from formflow.logic import (
    answer_status,
    follow_up_fallback,
    is_application_question,
    render_answer,
    render_official_card,
    status_icon,
    status_label,
    translated_suggestions,
)
from formflow.official import formflow_official_sources
from formflow.ollama_client import OLLAMA_REQUEST_TIMEOUT, OllamaError, generate_ollama_response
from formflow.services import formflow_services
from formflow.translations import (
    LANGUAGES,
    WELCOME_CONTENT,
    bank_ui_labels,
    bank_ui_labels_js,
    formflow_language_code,
    formflow_translations,
    formflow_ui_extras,
    t,
)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.json.ensure_ascii = False


class FormFlowValidationError(ValueError):
    """Mirrors PHP's InvalidArgumentException — a 400-level user error."""


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _trim(value):
    return (value or "").strip()


def _parse_answers(form):
    """Rebuilds the answers[key] bracket-notation fields PHP receives
    automatically as $_POST['answers'] into a plain dict."""
    answers = {}
    pattern = re.compile(r"^answers\[(.+)\]$")
    for key in form:
        match = pattern.match(key)
        if match:
            answers[match.group(1)] = form.get(key)
    return answers


def _parse_history(raw_history):
    history = []
    if not raw_history:
        return history
    try:
        decoded = json.loads(raw_history)
    except (TypeError, ValueError):
        return history
    if not isinstance(decoded, list):
        return history
    items = [item for item in decoded if isinstance(item, dict)][-4:]
    for item in items:
        history.append({
            "question": str(item.get("question", ""))[:400],
            "answer": str(item.get("answer", ""))[:1200],
        })
    return history


@app.errorhandler(500)
def handle_server_error(_error):
    return config.ERROR_PAGE_HTML, 500


# ---------------------------------------------------------------------------
# Home / apply / guidelines page  (index.php)
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    if "reset" in request.args:
        session.pop("formflow", None)

    services = formflow_services()
    banks = formflow_banks()
    kyc_purposes = formflow_kyc_purposes()
    translations = formflow_translations()
    initial_language = formflow_language_code(request.args.get("language", "en"))
    ui = translations[initial_language]
    mode = request.args.get("mode", "home")
    welcome = WELCOME_CONTENT[initial_language]

    client_translations = {}
    extras = formflow_ui_extras()
    for code, dictionary in translations.items():
        merged = dict(dictionary)
        merged.update(extras.get(code, {}))
        w = WELCOME_CONTENT.get(code, {})
        merged.update({
            "welcome_title": w.get("title", ""),
            "welcome_subtitle": w.get("subtitle", ""),
            "welcome_intro": w.get("intro", ""),
            "welcome_lead": w.get("lead", ""),
            "welcome_apply": w.get("apply", ""),
            "welcome_guidelines": w.get("guidelines", ""),
            "welcome_items": w.get("items", []),
        })
        client_translations[code] = merged

    service_groups = {}
    for name, service in services.items():
        service_groups.setdefault(service["category"], {})[name] = service

    return render_template(
        "index.html",
        ui=ui,
        languages=LANGUAGES,
        initial_language=initial_language,
        mode=mode,
        welcome=welcome,
        service_groups=service_groups,
        custom_placeholder=t("custom_placeholder", initial_language),
        footer_text=t("footer", initial_language),
        service_data_json=json.dumps(services, ensure_ascii=False),
        bank_data_json=json.dumps(banks, ensure_ascii=False),
        kyc_purposes_json=json.dumps(kyc_purposes, ensure_ascii=False),
        client_translations_json=json.dumps(client_translations, ensure_ascii=False),
        bank_ui_json=json.dumps(bank_ui_labels_js(), ensure_ascii=False),
    )


# ---------------------------------------------------------------------------
# Readiness analysis + result dashboard + downloads  (analyze.php)
# ---------------------------------------------------------------------------

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    services = formflow_services()
    official_sources = formflow_official_sources()
    banks = formflow_banks()
    kyc_purposes = formflow_kyc_purposes()
    session_state = session.get("formflow", {})

    form_type = _trim(request.form.get("form_type") or session_state.get("service_name") or "")
    language = formflow_language_code(_trim(request.form.get("language") or session_state.get("language") or "en"))
    ui_dict = formflow_translations()[language]
    language_name = ui_dict["name"]
    question = _trim(request.form.get("question") or "")
    answers = _parse_answers(request.form)
    history = _parse_history(request.form.get("history"))

    error_message = None
    status_code = 200
    answer = ""
    service = None
    checklist = []
    readiness = {"percent": 0, "label": "NEEDS PREPARATION", "tone": "red"}
    next_action = "Verify the current requirements with the relevant official authority."
    official = None
    is_app_question = False
    selected_bank = None
    kyc_purpose = ""

    # Guide download (GET /analyze?download=word|pdf)
    if request.method == "GET" and "download" in request.args and (session.get("formflow") or {}).get("guide"):
        guide = session["formflow"]["guide"]
        if request.args.get("download") == "word":
            data, filename, mimetype = build_word_document(guide)
            return Response(data, mimetype=mimetype, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
        if request.args.get("download") == "pdf":
            data, filename, mimetype = build_pdf_document(guide)
            return Response(data, mimetype=mimetype, headers={"Content-Disposition": f'attachment; filename="{filename}"'})

    try:
        if request.method != "POST":
            raise FormFlowValidationError(t("answer", language))
        if form_type not in services:
            raise FormFlowValidationError(t("choose", language))
        if language not in ("en", "ta", "hi", "ml"):
            raise FormFlowValidationError(t("language", language))
        if question == "":
            raise FormFlowValidationError(t("question", language))
        if len(question) > 8000:
            raise FormFlowValidationError("Please keep your question under 2,000 characters.")

        service = services[form_type]

        if form_type == "Bank KYC":
            bank_id = _trim(answers.get("bank_id", ""))
            if bank_id not in banks:
                raise FormFlowValidationError("Please select a bank for Bank KYC.")
            selected_bank = banks[bank_id]
            kyc_purpose = answers.get("kyc_purpose", "")
            if kyc_purpose not in kyc_purposes:
                raise FormFlowValidationError("Please select what you need for Bank KYC.")
            official = {
                "authority": selected_bank["bank_name"],
                "application_url": selected_bank["url"],
                "information_url": selected_bank["url"],
                "source_label": selected_bank["source"],
                "verified": selected_bank["verified"],
                "last_verified_date": "2026-09-04",
                "scope_note": "Use the selected bank\u2019s official channel. KYC availability and process may vary by purpose and bank.",
            }
        else:
            official = official_sources.get(form_type)

        is_app_question = is_application_question(question)

        session["formflow"] = {
            "service_id": form_type.lower().replace(" ", "_"),
            "service_name": form_type,
            "language": language,
            "intake": answers,
            "original_question": session_state.get("original_question", question),
            "conversation": history,
            "journey_stage": session_state.get("journey_stage", "Understand"),
            "official_application_url": (official or {}).get("application_url"),
            "official_information_url": (official or {}).get("information_url"),
            "authority": (official or {}).get("authority"),
            "source_name": (official or {}).get("source_label"),
            "verification_status": bool((official or {}).get("verified", False)),
            "last_verified_date": (official or {}).get("last_verified_date"),
            "selected_bank": (selected_bank or {}).get("id"),
            "selected_bank_name": (selected_bank or {}).get("bank_name"),
            "kyc_purpose": kyc_purpose,
        }

        for item in service["checklist"]:
            checklist.append({"label": item["label"], "status": answer_status(item, answers)})

        ready_count = sum(1 for item in checklist if item["status"] == "ready")
        prepare_count = sum(1 for item in checklist if item["status"] == "prepare")
        readiness["percent"] = round((ready_count / max(len(checklist), 1)) * 100)
        if prepare_count == 0 and readiness["percent"] >= 70:
            readiness["label"] = t("ready_status", language)
            readiness["tone"] = "green"
        elif readiness["percent"] >= 40:
            readiness["label"] = t("almost", language)
            readiness["tone"] = "yellow"
        else:
            readiness["label"] = t("needs", language)

        for item in checklist:
            if item["status"] == "prepare":
                next_action = t("prepare_status", language) + ": " + item["label"]
                break
            if item["status"] == "verify":
                next_action = t("conditional", language) + ": " + item["label"]

        answer_context = json.dumps({
            "answers": answers,
            "checklist": checklist,
            "readiness_estimate": readiness["label"],
            "bank": (selected_bank or {}).get("bank_name"),
            "kyc_purpose": kyc_purposes.get(kyc_purpose),
        }, ensure_ascii=False)
        history_context = "No earlier follow-up questions." if history == [] else json.dumps(history, ensure_ascii=False)
        is_follow_up = history != []
        response_instructions = (
            f"Answer this follow-up directly in {language_name} using short paragraphs and at most 3 bullet points. "
            "Start with ## Answer, then use ## What to do next. Do not repeat the entire readiness report."
            if is_follow_up else
            f"Write the entire answer in {language_name}. Use exactly these headings, each beginning with ##: "
            "## Readiness summary ## Prepare before you apply ## What happens next? ## Future steps ## Your next action."
        )
        direct_answer_instruction = (
            "Answer the user's application-location question first and clearly. Do not invent or output a URL; "
            "the application supplies the official link card separately."
            if is_app_question else
            "Answer the user\u2019s specific question first, then connect it to their preparation context."
        )
        prompt = f"""You are FormFlow AI, an Application Readiness and Journey Navigator.
Service: {form_type}
User language: {language_name}
User question: {question}
User intake and preparation estimate: {answer_context}
Previous conversation context: {history_context}

{response_instructions}
{direct_answer_instruction}

Explain the user's personalized situation from the intake. Be concise and practical. Mention missing or conditional items without claiming they are legally mandatory. Do not invent official requirements, eligibility, fees, deadlines, processing times, bank policies, test rules, alternatives, or URLs. Mark uncertain items as conditional and say: requirements may vary; verify current requirements with the relevant official authority, bank, provider, or state. For times, say only officially stated, estimated/may vary, or not confirmed when appropriate. Give exactly one immediate next action."""

        try:
            answer = generate_ollama_response(prompt, 90 if is_follow_up else 700, 35 if is_follow_up else OLLAMA_REQUEST_TIMEOUT)
        except OllamaError:
            if not is_follow_up and not is_app_question:
                raise
            answer = follow_up_fallback(form_type, question, next_action)

        history.append({"question": question, "answer": answer})
        history = history[-6:]
        session["formflow"]["conversation"] = history
        session["formflow"]["journey_stage"] = "Apply" if is_app_question else session["formflow"].get("journey_stage", "Understand")
        guide_name = (selected_bank["bank_name"] + " \u2014 KYC") if (form_type == "Bank KYC" and selected_bank) else form_type
        session["formflow"]["guide"] = formflow_guide_data(
            guide_name, language, checklist, readiness["label"], answer, next_action, official or {}, service["journey"]
        )
        session.modified = True

    except FormFlowValidationError as error:
        status_code = 400
        error_message = str(error)
    except OllamaError as error:
        status_code = 502
        error_message = str(error)
    except Exception as error:  # noqa: BLE001 - mirrors PHP's catch (Throwable $error)
        status_code = 502
        error_message = str(error)

    if error_message is not None:
        return render_template(
            "analyze.html",
            error_message=error_message,
            ui=lambda key: t(key, language),
            all_translations=formflow_translations(),
            language=language,
        ), status_code

    guide = session["formflow"].get("guide") or formflow_guide_data(
        form_type, language, checklist, readiness["label"], answer, next_action, official or {}, service["journey"]
    )
    answer_html = render_answer(answer)
    official_card_html = render_official_card(official, form_type, True, language)
    # NOTE: the original analyze.php only ever calls translatedSuggestions()
    # here; followUpSuggestions() is defined in the PHP source but never
    # invoked, so that behavior (or lack of it) is kept identical.
    suggestions = translated_suggestions(language, form_type, question)

    return render_template(
        "analyze.html",
        error_message=None,
        ui=lambda key: t(key, language),
        all_translations=formflow_translations(),
        language=language,
        form_type=form_type,
        service=service,
        selected_bank=selected_bank,
        bank_ui_labels=bank_ui_labels(),
        kyc_purpose=kyc_purpose,
        kyc_purposes=kyc_purposes,
        language_name=language_name,
        readiness=readiness,
        checklist=checklist,
        status_icon=status_icon,
        status_label=status_label,
        question=question,
        answer_html=answer_html,
        official_card_html=official_card_html,
        guide=guide,
        next_action=next_action,
        suggestions=suggestions,
        history_json=json.dumps(history, ensure_ascii=False),
        answers=answers,
    )


if __name__ == "__main__":
    app.run(debug=True)
