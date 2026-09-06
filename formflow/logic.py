"""Python port of the pure helper functions defined at the top of analyze.php."""

import re
from html import escape as e

from .translations import t


def translated_suggestions(language, service, question):
    if service == "Bank KYC":
        sets = {
            "en": ["Can I do this online?", "What documents should I prepare?", "What happens after submission?", "Do I need to visit a branch?", "Do I need to renew this later?"],
            "ta": ["இதை இணையத்தில் செய்ய முடியுமா?", "என்ன ஆவணங்களைத் தயாரிக்க வேண்டும்?", "சமர்ப்பித்த பிறகு என்ன நடக்கும்?", "நான் கிளைக்குச் செல்ல வேண்டுமா?", "இதை மீண்டும் புதுப்பிக்க வேண்டுமா?"],
            "hi": ["क्या यह ऑनलाइन किया जा सकता है?", "मुझे कौन से दस्तावेज़ तैयार करने चाहिए?", "जमा करने के बाद क्या होगा?", "क्या मुझे शाखा में जाना होगा?", "क्या इसे बाद में नवीनीकृत करना होगा?"],
            "ml": ["ഇത് ഓൺലൈനായി ചെയ്യാമോ?", "ഏത് രേഖകളാണ് തയ്യാറാക്കേണ്ടത്?", "സമർപ്പിച്ചതിന് ശേഷം എന്ത് സംഭവിക്കും?", "ഞാൻ ശാഖയിൽ പോകണമോ?", "ഇത് പിന്നീട് പുതുക്കണമോ?"],
        }
        return sets.get(language, [])

    sets = {
        "en": ["Show my personalized checklist", "I don't have one of these documents", "What should I prepare first?", "What happens after submission?", "Where do I apply?"],
        "ta": ["எனது தனிப்பயன் பட்டியலைக் காண்பிக்கவும்", "என்னிடம் ஒரு ஆவணம் இல்லை", "முதலில் நான் எதைத் தயாரிக்க வேண்டும்?", "விண்ணப்பித்த பிறகு என்ன நடக்கும்?", "நான் எங்கு விண்ணப்பிக்கலாம்?"],
        "hi": ["मेरी व्यक्तिगत सूची दिखाएँ", "मेरे पास एक दस्तावेज़ नहीं है", "मुझे पहले क्या तैयार करना चाहिए?", "आवेदन के बाद क्या होगा?", "मैं कहाँ आवेदन कर सकता हूँ?"],
        "ml": ["എന്റെ വ്യക്തിഗത പട്ടിക കാണിക്കുക", "എന്റെ പക്കൽ ഒരു രേഖയില്ല", "ആദ്യം ഞാൻ എന്ത് തയ്യാറാക്കണം?", "അപേക്ഷിച്ചതിന് ശേഷം എന്ത് സംഭവിക്കും?", "എവിടെയാണ് അപേക്ഷിക്കേണ്ടത്?"],
    }
    return sets.get(language, sets["en"])


def answer_status(item, answers):
    if item.get("status", "") == "verify":
        return "verify"
    value = str(answers.get(item.get("question", ""), ""))
    return "ready" if value == "yes" else ("prepare" if value == "no" else "verify")


def status_label(status, language):
    return {
        "ready": t("available", language),
        "prepare": t("prepare_status", language),
        "verify": t("conditional", language),
    }.get(status, t("conditional", language))


def status_icon(status):
    return {"ready": "\u2713", "prepare": "!", "verify": "?"}.get(status, "?")


_APPLICATION_PHRASES = [
    "where can i apply", "how do i apply", "application website", "official website",
    "where should i submit", "apply online", "online application", "application portal",
    "where do i apply",
]


def is_application_question(question):
    question = question.lower()
    return any(phrase in question for phrase in _APPLICATION_PHRASES)


def render_official_card(official, service, show_link, language):
    official = official or {}
    html = (
        '<section class="official-card mt-4"><div class="official-heading">'
        '<span class="official-emblem">&#127963;</span><div><p class="section-kicker mb-1">'
        + e(t("official", language)) + '</p><h3>' + e(official.get("authority") or "Relevant official authority") + '</h3></div>'
    )
    if official.get("verified") is True:
        html += '<span class="official-badge">&#10003; ' + e(t("source", language)) + '</span>'
    html += '</div><p class="official-source">' + e(t("source_label", language)) + ': ' + e(official.get("source_label") or t("unavailable", language)) + '</p>'
    if official.get("last_verified_date"):
        html += '<p class="official-verified">' + e(t("verified", language)) + ': ' + e(official["last_verified_date"]) + '</p>'
    if show_link and official.get("verified") is True and official.get("application_url"):
        html += '<a class="official-action" href="' + e(official["application_url"]) + '" target="_blank" rel="noopener noreferrer">&#128279; ' + e(t("open", language)) + ' <span>&#8599;</span></a>'
        if official.get("information_url"):
            html += '<a class="official-info" href="' + e(official["information_url"]) + '" target="_blank" rel="noopener noreferrer">&#8505; ' + e(t("info", language)) + '</a>'
    else:
        html += '<div class="official-unverified">' + e(t("unavailable", language)) + '</div>'
    html += '<p class="official-note">' + e(t("official_note", language)) + '</p></section>'
    return html


def follow_up_suggestions(service, question):
    question = question.lower()
    if "document" in question or "missing" in question:
        suggestions = ["Show my personalized checklist", "I don't have one of these documents", "What should I prepare first?"]
    elif "submit" in question or "after" in question:
        suggestions = ["What happens after submission?", "Is there another step after this?", "How might verification work?"]
    else:
        suggestions = ["Show my personalized checklist", "What document am I missing?", "What should I do next?"]

    if "Licence" in service:
        suggestions.append("What should I prepare for the test?")
    elif service == "Scholarship Application":
        suggestions.append("What should I check before submitting?")
    elif service == "Bank KYC":
        suggestions.append("Do I need to renew this later?")
    else:
        suggestions.append("What happens after submission?")

    suggestions.append("Where do I apply?")
    seen = []
    for item in suggestions:
        if item not in seen:
            seen.append(item)
    return seen


def follow_up_fallback(service, question, next_action):
    question = question.lower()
    if is_application_question(question):
        return (
            "## Where can you apply?\nThe controlled official application card below shows the verified portal "
            "when one is available for this service. Use it to check the current requirements and application "
            "process before submitting.\n\n## What to do next\nOpen the official application card below, confirm "
            "that it applies to your authority or jurisdiction, and then review your preparation checklist."
        )
    if "after" in question or "submit" in question:
        return (
            "## Answer\nAfter submission, the relevant authority, provider, or bank may review the information "
            "and supporting details. The exact verification steps, processing time, notifications, and outcome "
            "depend on the service and local authority.\n\n## What to do next\nKeep your submission reference or "
            "confirmation if one is provided, monitor the official channel, and verify any request for additional "
            "information.\n\n## Important note\nRequirements and processing details may vary. Verify the current "
            "process with the relevant official authority."
        )
    if "checklist" in question or "missing" in question or "document" in question:
        return (
            "## Answer\nYour checklist separates items you marked as ready from items that need preparation or "
            "official verification. A missing item does not automatically prove that a specific alternative will "
            "be accepted.\n\n## What to do next\nStart with the first item marked NEED TO PREPARE, or verify the "
            f"first item marked CONDITIONAL / VERIFY.\n\n## Important note\nAccepted documents and alternatives "
            f"may vary for {service}. Verify them with the relevant official authority."
        )
    return (
        f"## Answer\nYour readiness estimate is based only on the information you provided. Use the checklist and "
        f"journey stages to organize your preparation for {service}.\n\n## What to do next\n{next_action}\n\n"
        "## Important note\nVerify current requirements with the relevant official authority."
    )


_LIST_ITEM_RE = re.compile(r"^(?:[-*]|\d+[.)])\s+(.+)$")


def render_answer(answer):
    html = ""
    open_section = False
    in_list = False
    for raw_line in re.split(r"\r\n|\r|\n", answer.strip()):
        line = raw_line.strip()
        if line == "":
            if in_list:
                html += "</ul>"
                in_list = False
            continue
        if line.startswith("## "):
            if in_list:
                html += "</ul>"
                in_list = False
            if open_section:
                html += "</div></article>"
            html += '<article class="answer-section"><h3>' + e(line[3:].strip()) + '</h3><div class="answer-content">'
            open_section = True
            continue
        match = _LIST_ITEM_RE.match(line)
        if match:
            if not in_list:
                html += '<ul class="answer-list">'
                in_list = True
            html += "<li>" + e(match.group(1)) + "</li>"
            continue
        if in_list:
            html += "</ul>"
            in_list = False
        if not open_section:
            html += '<article class="answer-section"><div class="answer-content">'
            open_section = True
        html += "<p>" + e(line) + "</p>"
    if in_list:
        html += "</ul>"
    if open_section:
        html += "</div></article>"
    return html or "<p>No AI explanation was returned.</p>"
