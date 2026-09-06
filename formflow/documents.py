"""Python port of includes/documents.php."""

import os
import re
import subprocess
import tempfile
from html import escape as e


def formflow_document_labels(language):
    labels = {
        "en": {"title": "Download Your Guide", "description": "Save your personalized application procedure and checklist for offline use.", "pdf": "Download PDF", "word": "Download Word", "what_do": "What to do", "what_not": "What not to do", "checklist": "Application preparation checklist", "available": "Available", "prepare": "Need to prepare", "verify": "Conditional / verify", "stage": "Current journey stage", "important": "Important note", "disclaimer": "FormFlow AI provides guidance for preparation and does not replace instructions from the official authority.", "official_unavailable": "Official application link is not currently available in the trusted configuration.", "next": "Your next action"},
        "ta": {"title": "உங்கள் வழிகாட்டியைப் பதிவிறக்கவும்", "description": "உங்கள் தனிப்பயன் விண்ணப்ப நடைமுறை மற்றும் பட்டியலை இணையமின்றி பயன்படுத்த சேமிக்கவும்.", "pdf": "PDF பதிவிறக்கம்", "word": "Word பதிவிறக்கம்", "what_do": "செய்ய வேண்டியது", "what_not": "செய்யக் கூடாதது", "checklist": "விண்ணப்பத் தயார்நிலைப் பட்டியல்", "available": "கிடைக்கிறது", "prepare": "தயாரிக்க வேண்டும்", "verify": "நிபந்தனை / சரிபார்க்கவும்", "stage": "தற்போதைய பயணக் கட்டம்", "important": "முக்கிய குறிப்பு", "disclaimer": "FormFlow AI தயாரிப்புக்கான வழிகாட்டுதலை வழங்குகிறது; இது அதிகாரப்பூர்வ அதிகாரத்தின் அறிவுறுத்தல்களை மாற்றாது.", "official_unavailable": "நம்பகமான அமைப்பில் அதிகாரப்பூர்வ விண்ணப்ப இணைப்பு தற்போது கிடைக்கவில்லை.", "next": "உங்கள் அடுத்த செயல்"},
        "hi": {"title": "अपना मार्गदर्शक डाउनलोड करें", "description": "अपनी व्यक्तिगत आवेदन प्रक्रिया और सूची को ऑफलाइन उपयोग के लिए सहेजें।", "pdf": "PDF डाउनलोड करें", "word": "Word डाउनलोड करें", "what_do": "क्या करें", "what_not": "क्या न करें", "checklist": "आवेदन तैयारी सूची", "available": "उपलब्ध", "prepare": "तैयारी आवश्यक", "verify": "सशर्त / सत्यापित करें", "stage": "वर्तमान यात्रा चरण", "important": "महत्वपूर्ण नोट", "disclaimer": "FormFlow AI तैयारी के लिए मार्गदर्शन देता है और आधिकारिक प्राधिकरण के निर्देशों का स्थान नहीं लेता।", "official_unavailable": "विश्वसनीय कॉन्फ़िगरेशन में आधिकारिक आवेदन लिंक अभी उपलब्ध नहीं है।", "next": "आपका अगला कार्य"},
        "ml": {"title": "നിങ്ങളുടെ മാർഗ്ഗനിർദ്ദേശം ഡൗൺലോഡ് ചെയ്യുക", "description": "നിങ്ങളുടെ വ്യക്തിഗത അപേക്ഷാ നടപടിക്രമവും പട്ടികയും ഓഫ്‌ലൈനായി ഉപയോഗിക്കാൻ സേവ് ചെയ്യുക.", "pdf": "PDF ഡൗൺലോഡ് ചെയ്യുക", "word": "Word ഡൗൺലോഡ് ചെയ്യുക", "what_do": "ചെയ്യേണ്ടത്", "what_not": "ചെയ്യരുതാത്തത്", "checklist": "അപേക്ഷാ തയ്യാറെടുപ്പ് പട്ടിക", "available": "ലഭ്യമാണ്", "prepare": "തയ്യാറാക്കണം", "verify": "നിബന്ധന / പരിശോധിക്കുക", "stage": "നിലവിലെ യാത്രാ ഘട്ടം", "important": "പ്രധാന കുറിപ്പ്", "disclaimer": "FormFlow AI തയ്യാറെടുപ്പിനുള്ള മാർഗ്ഗനിർദ്ദേശം നൽകുന്നു; ഇത് ഔദ്യോഗിക അധികാരിയുടെ നിർദ്ദേശങ്ങൾക്ക് പകരമല്ല.", "official_unavailable": "വിശ്വസനീയമായ ക്രമീകരണത്തിൽ ഔദ്യോഗിക അപേക്ഷാ ലിങ്ക് നിലവിൽ ലഭ്യമല്ല.", "next": "നിങ്ങളുടെ അടുത്ത നടപടി"},
    }
    return labels.get(language, labels["en"])


_SENSITIVE_PATTERN = re.compile(
    r"\b(password|passcode|otp|one[- ]time password|pin|login credential)\b[^.\n]*",
    re.IGNORECASE,
)


def formflow_guide_data(service_name, language, checklist, readiness, answer, next_action, official, journey):
    labels = formflow_document_labels(language)
    do = {
        "en": ["Keep your available information ready.", "Review details before submitting.", "Use the trusted official portal when one is configured.", "Keep a submission reference if the authority provides one."],
        "ta": ["உங்களிடம் உள்ள தகவல்களைத் தயாராக வைத்திருங்கள்.", "சமர்ப்பிப்பதற்கு முன் விவரங்களைச் சரிபார்க்கவும்.", "உள்ளமைக்கப்பட்ட நம்பகமான அதிகாரப்பூர்வ தளத்தைப் பயன்படுத்தவும்.", "அதிகாரம் வழங்கும் சமர்ப்பிப்பு எண்ணை சேமிக்கவும்."],
        "hi": ["उपलब्ध जानकारी तैयार रखें।", "जमा करने से पहले विवरण जाँचें।", "कॉन्फ़िगर किए गए विश्वसनीय आधिकारिक पोर्टल का उपयोग करें।", "प्राधिकरण द्वारा दिया गया संदर्भ सुरक्षित रखें।"],
        "ml": ["ലഭ്യമായ വിവരങ്ങൾ തയ്യാറാക്കി വയ്ക്കുക.", "സമർപ്പിക്കുന്നതിന് മുമ്പ് വിവരങ്ങൾ പരിശോധിക്കുക.", "ക്രമീകരിച്ച വിശ്വസനീയമായ ഔദ്യോഗിക പോർട്ടൽ ഉപയോഗിക്കുക.", "അധികാരം നൽകുന്ന റഫറൻസ് സൂക്ഷിക്കുക."],
    }.get(language, [])
    dont = {
        "en": ["Do not enter incorrect personal information.", "Do not submit incomplete information.", "Do not share OTPs, passwords, PINs, or login credentials.", "Do not rely on unofficial application links."],
        "ta": ["தவறான தனிப்பட்ட தகவல்களை உள்ளிட வேண்டாம்.", "முழுமையற்ற தகவல்களை சமர்ப்பிக்க வேண்டாம்.", "OTP, கடவுச்சொல், PIN அல்லது உள்நுழைவு தகவல்களை பகிர வேண்டாம்.", "அதிகாரப்பூர்வமற்ற விண்ணப்ப இணைப்புகளை நம்ப வேண்டாம்."],
        "hi": ["गलत व्यक्तिगत जानकारी दर्ज न करें।", "अधूरी जानकारी जमा न करें।", "OTP, पासवर्ड, PIN या लॉगिन जानकारी साझा न करें।", "अनौपचारिक आवेदन लिंक पर भरोसा न करें।"],
        "ml": ["തെറ്റായ വ്യക്തിഗത വിവരങ്ങൾ നൽകരുത്.", "പൂർണ്ണമല്ലാത്ത വിവരങ്ങൾ സമർപ്പിക്കരുത്.", "OTP, പാസ്‌വേഡ്, PIN അല്ലെങ്കിൽ ലോഗിൻ വിവരങ്ങൾ പങ്കിടരുത്.", "ഔദ്യോഗികമല്ലാത്ത അപേക്ഷാ ലിങ്കുകളിൽ വിശ്വസിക്കരുത്."],
    }.get(language, [])

    answer = _SENSITIVE_PATTERN.sub("[sensitive information omitted]", answer)
    next_action = _SENSITIVE_PATTERN.sub("[sensitive information omitted]", next_action)

    return {
        "serviceName": service_name,
        "language": language,
        "checklist": checklist,
        "readiness": readiness,
        "answer": answer,
        "nextAction": next_action,
        "official": official,
        "journey": journey,
        "labels": labels,
        "do": do,
        "dont": dont,
    }


def formflow_safe_filename(service_name, extension):
    name = re.sub(r"[^A-Za-z0-9]+", "_", service_name) or "Application"
    return "FormFlow_" + name.strip("_") + "_Guide." + extension


def _strip_tags(value):
    return re.sub(r"<[^>]*>", "", value)


def formflow_guide_text(guide):
    lines = [
        "FormFlow AI",
        guide["serviceName"] + " \u2014 Application Guide",
        "",
        guide["labels"]["stage"] + ": " + (guide["journey"][0] if guide["journey"] else ""),
        "Readiness: " + guide["readiness"],
        "",
        "ANSWER",
        _strip_tags(guide["answer"]),
        "",
        guide["labels"]["checklist"].upper(),
    ]
    for item in guide["checklist"]:
        lines.append("[" + item["status"].upper() + "] " + item["label"])
    lines.append("")
    lines.append(guide["labels"]["what_do"].upper())
    for item in guide["do"]:
        lines.append("+ " + item)
    lines.append("")
    lines.append(guide["labels"]["what_not"].upper())
    for item in guide["dont"]:
        lines.append("- " + item)
    lines.append("")
    lines.append(guide["labels"]["next"].upper())
    lines.append(guide["nextAction"])
    lines.append("")
    lines.append(guide["labels"]["important"].upper())
    lines.append(guide["labels"]["disclaimer"])
    official = guide.get("official") or {}
    if official.get("verified") and official.get("application_url"):
        lines.append("Official URL: " + official["application_url"])
        lines.append("Source: " + (official.get("source_label") or ""))
        lines.append("Last verified: " + (official.get("last_verified_date") or ""))
    else:
        lines.append(guide["labels"]["official_unavailable"])
    return "\n".join(lines)


def build_word_document(guide):
    """Returns (bytes, filename, mimetype) — same .doc-as-html trick the PHP used."""
    text = formflow_guide_text(guide)
    html = (
        '<html><head><meta charset="UTF-8"><title>FormFlow AI \u2014 Application Guide</title></head>'
        '<body><pre style="font-family:Arial;white-space:pre-wrap">' + e(text) + "</pre></body></html>"
    )
    filename = formflow_safe_filename(guide["serviceName"], "doc")
    return html.encode("utf-8"), filename, "application/msword; charset=UTF-8"


def _build_guide_html(guide):
    checklist_items = "".join(
        '<li><strong>[' + e(item["status"].upper()) + ']</strong> ' + e(item["label"]) + '</li>'
        for item in guide["checklist"]
    )
    do_items = "".join('<li>\u2713 ' + e(item) + '</li>' for item in guide["do"])
    dont_items = "".join('<li>\u2717 ' + e(item) + '</li>' for item in guide["dont"])
    official = guide.get("official") or {}
    if official.get("verified") and official.get("application_url"):
        official_section = (
            '<h2>' + e(guide["labels"]["official_unavailable"]) + '</h2>'
            '<p><a href="' + e(official["application_url"]) + '">' + e(official["application_url"]) + '</a></p>'
            '<p>' + e(official.get("source_label") or "") + '<br>' + e(official.get("last_verified_date") or "") + '</p>'
        )
    else:
        official_section = '<h2>' + e(guide["labels"]["official_unavailable"]) + '</h2>'

    answer_html = _strip_tags(guide["answer"]).replace("\n", "<br>\n")
    return (
        '<!doctype html><html lang="' + e(guide["language"]) + '"><head><meta charset="UTF-8">'
        '<style>body{font-family:Arial,"Noto Sans",sans-serif;margin:42px;color:#17212b}'
        'h1{color:#0e4d40;border-bottom:2px solid #176b58;padding-bottom:10px}'
        'h2{color:#176b58;margin-top:26px}li{margin:7px 0}'
        '.meta{padding:12px;background:#eef5ef}'
        '.note{padding:12px;background:#fff8e8;border-left:4px solid #f4c96b}a{color:#176b58}</style></head><body>'
        '<h1>FormFlow AI</h1><h2>' + e(guide["serviceName"]) + ' \u2014 Application Guide</h2>'
        '<div class="meta"><strong>' + e(guide["labels"]["stage"]) + ':</strong> '
        + e(guide["journey"][0] if guide["journey"] else "") + '<br><strong>Readiness:</strong> ' + e(guide["readiness"]) + '</div>'
        '<h2>Answer</h2><p>' + answer_html + '</p>'
        '<h2>' + e(guide["labels"]["checklist"]) + '</h2><ul>' + checklist_items + '</ul>'
        '<h2>' + e(guide["labels"]["what_do"]) + '</h2><ul>' + do_items + '</ul>'
        '<h2>' + e(guide["labels"]["what_not"]) + '</h2><ul>' + dont_items + '</ul>'
        '<h2>' + e(guide["labels"]["next"]) + '</h2><p>' + e(guide["nextAction"]) + '</p>'
        '<h2>' + e(guide["labels"]["important"]) + '</h2><div class="note">' + e(guide["labels"]["disclaimer"]) + '</div>'
        + official_section +
        '</body></html>'
    )


def _headless_browser_path():
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def _render_pdf_with_browser(guide):
    browser = _headless_browser_path()
    if browser is None:
        return None
    html = _build_guide_html(guide)
    with tempfile.TemporaryDirectory(prefix="formflow-guide-") as tmpdir:
        html_path = os.path.join(tmpdir, "guide.html")
        pdf_path = os.path.join(tmpdir, "guide.pdf")
        with open(html_path, "w", encoding="utf-8") as handle:
            handle.write(html)
        command = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--print-to-pdf=" + pdf_path,
            "file:///" + html_path.replace("\\", "/"),
        ]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        except (subprocess.SubprocessError, OSError):
            return None
        if os.path.isfile(pdf_path) and os.path.getsize(pdf_path) > 100:
            with open(pdf_path, "rb") as handle:
                return handle.read()
    return None


def _build_minimal_pdf_bytes(guide):
    """Hand-rolled fallback PDF writer, ported line-for-line from the PHP
    fallback that hand-writes raw PDF objects (no external dependency)."""
    text = re.sub(r"[^\x20-\x7E\r\n]", "?", formflow_guide_text(guide))
    stream = "BT /F1 10 Tf 45 760 Td 14 TL\n"
    for line in re.split(r"\r\n|\r|\n", text):
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream += "(" + escaped[:105] + ") Tj T*\n"
    stream += "ET"

    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        "<< /Length " + str(len(stream)) + " >>\nstream\n" + stream + "\nendstream",
    ]
    pdf = "%PDF-1.4\n"
    offsets = [0]
    for index, obj in enumerate(objects):
        offsets.append(len(pdf.encode("latin-1", errors="replace")))
        pdf += f"{index + 1} 0 obj\n{obj}\nendobj\n"
    xref = len(pdf.encode("latin-1", errors="replace"))
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
    for i in range(1, len(objects) + 1):
        pdf += f"{offsets[i]:010d} 00000 n \n"
    pdf += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    return pdf.encode("latin-1", errors="replace")


def build_pdf_document(guide):
    """Returns (bytes, filename, mimetype)."""
    pdf_bytes = _render_pdf_with_browser(guide)
    if pdf_bytes is None:
        pdf_bytes = _build_minimal_pdf_bytes(guide)
    filename = formflow_safe_filename(guide["serviceName"], "pdf")
    return pdf_bytes, filename, "application/pdf"
