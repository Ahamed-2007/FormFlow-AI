<?php
declare(strict_types=1);
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/includes/services.php';
require_once __DIR__ . '/includes/translations.php';
require_once __DIR__ . '/includes/banks.php';
if (isset($_GET['reset'])) unset($_SESSION['formflow']);
$services = formFlowServices();
$banks = formFlowBanks();
$kycPurposes = formFlowKycPurposes();
$languages = ['en' => 'English', 'ta' => 'தமிழ்', 'hi' => 'हिन्दी', 'ml' => 'മലയാളം'];
$translations = formFlowTranslations();
$initialLanguage = formFlowLanguageCode((string) ($_GET['language'] ?? 'en'));
$ui = $translations[$initialLanguage];
$mode = (string) ($_GET['mode'] ?? 'home');
$welcome = [
    'en' => ['title'=>'Welcome to FormFlow AI','subtitle'=>'Your Application Readiness & Journey Navigator','intro'=>'Get simple guidance for applications, certificates and important services.','lead'=>'With FormFlow AI, you can:','items'=>['Understand what you need','Prepare your documents and information','Understand the application procedure','Know what to do next','Follow your application journey','Download your personalized guide'],'apply'=>'I want to apply','guidelines'=>'I need guidelines'],
    'ta' => ['title'=>'வணக்கம்! FormFlow AI-க்கு வரவேற்கிறோம்','subtitle'=>'உங்கள் விண்ணப்பத் தயார்நிலை மற்றும் பயண வழிகாட்டி','intro'=>'விண்ணப்பங்கள், சான்றிதழ்கள் மற்றும் முக்கிய சேவைகளுக்கான எளிய வழிகாட்டுதலைப் பெறுங்கள்.','lead'=>'FormFlow AI மூலம் நீங்கள்:','items'=>['என்ன தேவை என்பதை அறியலாம்','தேவையான ஆவணங்களையும் தகவல்களையும் தயாரிக்கலாம்','விண்ணப்ப செயல்முறையைப் புரிந்துகொள்ளலாம்','அடுத்து என்ன செய்ய வேண்டும் என்பதை அறியலாம்','உங்கள் விண்ணப்பப் பயணத்தைப் பின்தொடரலாம்','தனிப்பயனாக்கப்பட்ட வழிகாட்டியைப் பதிவிறக்கலாம்'],'apply'=>'விண்ணப்பிக்க வேண்டும்','guidelines'=>'வழிகாட்டுதல் வேண்டும்'],
    'hi' => ['title'=>'FormFlow AI में आपका स्वागत है','subtitle'=>'आपका आवेदन तैयारी और यात्रा मार्गदर्शक','intro'=>'आवेदन, प्रमाणपत्र और महत्वपूर्ण सेवाओं के लिए सरल मार्गदर्शन पाएँ।','lead'=>'FormFlow AI से आप:','items'=>['जान सकते हैं कि क्या चाहिए','दस्तावेज़ और जानकारी तैयार कर सकते हैं','आवेदन प्रक्रिया समझ सकते हैं','जान सकते हैं कि आगे क्या करना है','अपनी आवेदन यात्रा देख सकते हैं','अपना व्यक्तिगत मार्गदर्शक डाउनलोड कर सकते हैं'],'apply'=>'मैं आवेदन करना चाहता हूँ','guidelines'=>'मुझे मार्गदर्शन चाहिए'],
    'ml' => ['title'=>'FormFlow AI-ലേക്ക് സ്വാഗതം','subtitle'=>'നിങ്ങളുടെ അപേക്ഷാ തയ്യാറെടുപ്പും യാത്രാ മാർഗ്ഗനിർദ്ദേശവും','intro'=>'അപേക്ഷകൾക്കും സർട്ടിഫിക്കറ്റുകൾക്കും പ്രധാന സേവനങ്ങൾക്കുമായി ലളിതമായ മാർഗ്ഗനിർദ്ദേശം നേടുക.','lead'=>'FormFlow AI ഉപയോഗിച്ച് നിങ്ങൾക്ക്:','items'=>['എന്താണ് ആവശ്യമെന്ന് മനസ്സിലാക്കാം','രേഖകളും വിവരങ്ങളും തയ്യാറാക്കാം','അപേക്ഷാ നടപടിക്രമം മനസ്സിലാക്കാം','അടുത്തതായി എന്ത് ചെയ്യണമെന്ന് അറിയാം','നിങ്ങളുടെ അപേക്ഷാ യാത്ര പിന്തുടരാം','വ്യക്തിഗത മാർഗ്ഗനിർദ്ദേശം ഡൗൺലോഡ് ചെയ്യാം'],'apply'=>'ഞാൻ അപേക്ഷിക്കണം','guidelines'=>'എനിക്ക് മാർഗ്ഗനിർദ്ദേശം വേണം'],
][$initialLanguage];
$clientTranslations = [];
foreach ($translations as $code => $dictionary) {
    $clientTranslations[$code] = array_merge($dictionary, formFlowUiExtras()[$code] ?? [], ['welcome_title'=>$welcome[$code]['title'] ?? '', 'welcome_subtitle'=>$welcome[$code]['subtitle'] ?? '', 'welcome_intro'=>$welcome[$code]['intro'] ?? '', 'welcome_lead'=>$welcome[$code]['lead'] ?? '', 'welcome_apply'=>$welcome[$code]['apply'] ?? '', 'welcome_guidelines'=>$welcome[$code]['guidelines'] ?? '', 'welcome_items'=>$welcome[$code]['items'] ?? []]);
}
$serviceGroups = [];
foreach ($services as $name => $service) {
    $serviceGroups[$service['category']][$name] = $service;
}
function e(string $value): string { return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function tx(string $key): string { global $initialLanguage; return t($key, $initialLanguage); }
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FormFlow AI | Application Readiness &amp; Journey Navigator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark app-nav"><div class="container py-2"><a class="navbar-brand fw-bold" href="index.php"><span class="brand-mark">F</span> FormFlow AI</a><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#appNav" aria-controls="appNav" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="appNav"><ul class="navbar-nav ms-auto align-items-lg-center gap-lg-2"><li class="nav-item"><a class="nav-link" data-i18n="home" href="index.php"><?= e($ui['home']) ?></a></li><li class="nav-item"><a class="nav-link" href="index.php?mode=apply&amp;language=<?= e($initialLanguage) ?>#analysis-form">Application</a></li><li class="nav-item"><a class="nav-link" href="index.php?mode=guidelines&amp;language=<?= e($initialLanguage) ?>#analysis-form">Guidelines</a></li><li class="nav-item"><a class="nav-link" data-i18n="how" href="#how-it-works"><?= e($ui['how']) ?></a></li><li class="nav-item"><a class="nav-link" data-i18n="about" href="#about"><?= e($ui['about']) ?></a></li><li class="nav-item"><label class="visually-hidden" for="nav-language">Language</label><select id="nav-language" class="nav-language-select" aria-label="Language selector"><?php foreach ($languages as $value => $label): ?><option value="<?= e($value) ?>"<?= $value === $initialLanguage ? ' selected' : '' ?>><?= e($label) ?></option><?php endforeach; ?></select></li></ul></div></div></nav>
<?php if ($mode === 'home'): ?>
<main>
<section class="welcome-hero"><div class="container"><div class="welcome-shell"><span class="eyebrow">FORMFLOW AI</span><h1 data-i18n="welcome_title"><?= e($welcome['title']) ?></h1><p class="welcome-subtitle" data-i18n="welcome_subtitle"><?= e($welcome['subtitle']) ?></p><p class="hero-copy" data-i18n="welcome_intro"><?= e($welcome['intro']) ?></p><div class="welcome-benefits"><p class="section-kicker" data-i18n="welcome_lead"><?= e($welcome['lead']) ?></p><div class="row g-3"><?php foreach ($welcome['items'] as $index => $item): ?><div class="col-md-6"><div class="benefit-item" data-welcome-index="<?= $index ?>"><span>✓</span><?= e($item) ?></div></div><?php endforeach; ?></div></div><div class="welcome-actions"><a id="apply-action" class="btn btn-primary btn-lg" href="index.php?mode=apply&amp;language=<?= e($initialLanguage) ?>#analysis-form" data-i18n="welcome_apply"><?= e($welcome['apply']) ?> <span>→</span></a><a id="guidelines-action" class="btn btn-outline-primary btn-lg" href="index.php?mode=guidelines&amp;language=<?= e($initialLanguage) ?>#analysis-form" data-i18n="welcome_guidelines"><?= e($welcome['guidelines']) ?> <span>→</span></a></div></div></div></section>
<section class="about-strip" id="about"><div class="container"><p class="section-kicker mb-2"><?= e($ui['about']) ?></p><h2><?= e($ui['navigator']) ?></h2><p><?= e($welcome['intro']) ?></p></div></section>
</main>
<?php else: ?>
<main>
<section class="hero">
    <div class="container">
        <div class="row align-items-end g-4">
            <div class="col-lg-7">
                <span class="eyebrow" data-i18n="understand">UNDERSTAND &middot; PREPARE &middot; APPLY</span>
                <h1 data-i18n="navigator">Don’t just understand the form.<br><span>Know if you’re ready to apply.</span></h1>
                <p class="hero-copy" data-i18n="about_text">FormFlow AI turns an uncertain application into a personalized readiness check, practical checklist, and clear next step.</p>
            </div>
            <div class="col-lg-5"><div class="journey-note"><div class="note-dot"></div><div><strong data-i18n="journey_note">Your application journey, organized.</strong><br><small data-i18n="official_note">General guidance only. Verify current requirements with the relevant authority, bank, provider, or state.</small></div></div></div>
        </div>

        <div class="flow-rail my-5"><span class="active">01 Choose</span><i></i><span>02 Check</span><i></i><span>03 Prepare</span><i></i><span>04 Apply</span><i></i><span>05 Follow through</span></div>

        <div class="card main-card">
            <div class="card-body p-4 p-md-5">
                <div class="d-flex justify-content-between align-items-start gap-3 mb-4"><div><p class="section-kicker mb-1" data-i18n="start">START YOUR READINESS CHECK</p><h2 class="h3 mb-0" data-i18n="tell">Tell us where you are</h2></div><span class="step-count">01 / 03</span></div>
                <form action="analyze.php" method="POST" id="analysis-form">
                    <div class="mb-4"><label for="form_type" class="form-label" data-i18n="choose"><?= e($ui['choose']) ?></label><select id="form_type" name="form_type" class="form-select form-select-lg" required><option value="" selected disabled>Select the application you want to prepare for</option><?php foreach ($serviceGroups as $category => $items): ?><optgroup label="<?= e($category) ?>"><?php foreach ($items as $name => $service): ?><option value="<?= e($name) ?>"><?= e($name) ?></option><?php endforeach; ?></optgroup><?php endforeach; ?></select><div id="service-description" class="service-description" hidden></div></div>
                    <div class="mb-4"><label for="language" class="form-label" data-i18n="language"><?= e($ui['language']) ?></label><select id="language" name="language" class="form-select form-select-lg" required><?php foreach ($languages as $value => $label): ?><option value="<?= e($value) ?>"><?= e($label) ?></option><?php endforeach; ?></select><div class="form-text">Your readiness summary and AI explanation will be written in this language.</div></div>
                    <div id="bank-kyc-panel" class="bank-kyc-panel" hidden></div>
                    <div id="question-panel" class="question-panel" hidden><div class="panel-heading"><div><p class="section-kicker mb-1" data-i18n="current">YOUR CURRENT POSITION</p><h3 class="h5 mb-0" data-i18n="questions">A few relevant questions</h3></div><span class="question-count" id="question-count"></span></div><div id="dynamic-questions"></div></div>
                    <div class="mb-4"><label for="question" class="form-label" data-i18n="clarify"><?= e($ui['question']) ?></label><textarea id="question" name="question" class="form-control question-box" rows="3" maxlength="2000" placeholder="<?= e(tx('custom_placeholder')) ?>" required></textarea><div class="form-text" data-i18n="question_help">Ask about documents, fields, submission, missing items, or future steps.</div></div>
                    <div class="privacy-note"><strong><?= e($ui['privacy_title']) ?>:</strong> <?= e($ui['privacy']) ?></div>
                    <div class="d-grid d-sm-flex justify-content-sm-end align-items-center gap-3 mt-4"><span class="small text-muted d-none d-sm-inline">FormFlow creates a preparation estimate, not an official decision.</span><button type="submit" class="btn btn-primary btn-lg px-4" id="analyze-button"><span data-i18n="analyze"><?= e($ui['analyze']) ?></span><span class="button-arrow">&#8594;</span></button></div>
                    <div class="loading-panel" id="loading-panel" aria-live="polite" hidden><span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span data-i18n="loading"><?= e($ui['loading']) ?></span></div>
                </form>
            </div>
        </div>
    </div>
</section>
<section class="feature-strip" id="how-it-works"><div class="container"><div class="row g-4"><div class="col-md-4"><div class="feature-item"><span class="feature-number">01</span><div><h3>Check</h3><p>See what you have, what needs preparation, and what must be verified.</p></div></div></div><div class="col-md-4"><div class="feature-item"><span class="feature-number">02</span><div><h3>Prepare</h3><p>Turn missing items into one clear, practical next action.</p></div></div></div><div class="col-md-4"><div class="feature-item"><span class="feature-number">03</span><div><h3>Follow through</h3><p>Understand verification, processing, outcomes, and future stages.</p></div></div></div></div></div></section>
<section class="about-strip" id="about"><div class="container"><p class="section-kicker mb-2">ABOUT FORMFLOW AI</p><h2>Clarity before you apply.</h2><p>FormFlow AI uses your answers to organize preparation and next steps. It is general guidance, not an official eligibility decision or a substitute for current authority instructions.</p></div></section>
<?php endif; ?></main>
<footer class="text-center py-4"><small data-i18n="footer"><?= e(tx('footer')) ?></small></footer>
<script>
const serviceData = <?= json_encode($services, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) ?>;
const bankData = <?= json_encode($banks, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) ?>;
const kycPurposes = <?= json_encode($kycPurposes, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) ?>;
const translations = <?= json_encode($clientTranslations, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) ?>;
const formSelect = document.getElementById('form_type');
const questionPanel = document.getElementById('question-panel');
const questions = document.getElementById('dynamic-questions');
const description = document.getElementById('service-description');
const questionCount = document.getElementById('question-count');
const bankPanel = document.getElementById('bank-kyc-panel');
const bankUi = { en: { bank: 'Select your bank', purpose: 'What do you need?', other: 'Enter your bank name', placeholder: 'Search bank name or short name' }, ta: { bank: 'உங்கள் வங்கியைத் தேர்ந்தெடுக்கவும்', purpose: 'உங்களுக்கு என்ன தேவை?', other: 'உங்கள் வங்கியின் பெயரை உள்ளிடுங்கள்', placeholder: 'வங்கியின் பெயரைத் தேடுங்கள்' }, hi: { bank: 'अपना बैंक चुनें', purpose: 'आपको क्या चाहिए?', other: 'अपने बैंक का नाम लिखें', placeholder: 'बैंक का नाम खोजें' }, ml: { bank: 'നിങ്ങളുടെ ബാങ്ക് തിരഞ്ഞെടുക്കുക', purpose: 'നിങ്ങൾക്ക് എന്താണ് വേണ്ടത്?', other: 'നിങ്ങളുടെ ബാങ്കിന്റെ പേര് നൽകുക', placeholder: 'ബാങ്കിന്റെ പേര് തിരയുക' } };
function renderBankPanel() { const isBank = formSelect.value === 'Bank KYC'; bankPanel.hidden = !isBank; if (!isBank) { bankPanel.innerHTML = ''; return; } const lang = document.getElementById('language').value || 'en'; const labels = bankUi[lang] || bankUi.en; let options = '<option value="" selected disabled>' + labels.placeholder + '</option>'; Object.values(bankData).forEach(function (bank) { options += '<option value="' + bank.id + '">' + bank.bank_name + (bank.short_name ? ' (' + bank.short_name + ')' : '') + '</option>'; }); bankPanel.innerHTML = '<div class="bank-fields"><div><label class="form-label">' + labels.bank + '</label><input list="bank-options" id="bank-search" class="form-control" placeholder="' + labels.placeholder + '" autocomplete="off"><datalist id="bank-options">' + Object.values(bankData).map(function (bank) { return '<option value="' + bank.bank_name + '" data-bank-id="' + bank.id + '">' + bank.short_name + '</option>'; }).join('') + '</datalist><input type="hidden" name="answers[bank_id]" id="bank-id"><input type="hidden" name="answers[bank_name]" id="bank-name"></div><div><label class="form-label">' + labels.purpose + '</label><select name="answers[kyc_purpose]" class="form-select" required><option value="" selected disabled>' + labels.purpose + '</option>' + Object.entries(kycPurposes).map(function (entry) { return '<option value="' + entry[0] + '">' + entry[1] + '</option>'; }).join('') + '</select></div><div id="other-bank-wrap" hidden><label class="form-label">' + labels.other + '</label><input name="answers[other_bank_name]" class="form-control" maxlength="120"></div></div>'; const search = document.getElementById('bank-search'); search.addEventListener('change', function () { const bank = Object.values(bankData).find(function (item) { return item.bank_name.toLowerCase() === search.value.toLowerCase() || item.short_name.toLowerCase() === search.value.toLowerCase(); }); document.getElementById('bank-id').value = bank ? bank.id : ''; document.getElementById('bank-name').value = bank ? bank.bank_name : ''; document.getElementById('other-bank-wrap').hidden = !bank || bank.id !== 'other'; }); }
function renderQuestions() {
    const service = serviceData[formSelect.value];
    questions.innerHTML = '';
    if (!service) { questionPanel.hidden = true; description.hidden = true; return; }
    description.textContent = service.description;
    description.hidden = false;
    questionPanel.hidden = false;
    questionCount.textContent = service.questions.length + ' questions';
    service.questions.forEach((item, index) => {
        const wrapper = document.createElement('div'); wrapper.className = 'dynamic-question';
        const label = document.createElement('label'); label.className = 'form-label'; label.textContent = (index + 1) + '. ' + item.label; wrapper.appendChild(label);
        if (item.type === 'text') {
            const input = document.createElement('input'); input.type = 'text'; input.name = 'answers[' + item.key + ']'; input.className = 'form-control'; input.placeholder = item.placeholder || ''; input.maxLength = 500; wrapper.appendChild(input);
        } else {
            const options = document.createElement('div'); options.className = 'choice-grid';
            Object.entries(item.options).forEach(([value, labelText]) => { const label = document.createElement('label'); label.className = 'choice-option'; label.innerHTML = '<input type="radio" name="answers[' + item.key + ']" value="' + value + '" required><span>' + labelText + '</span>'; options.appendChild(label); });
            wrapper.appendChild(options);
        }
        questions.appendChild(wrapper);
    });
}
formSelect.addEventListener('change', function () { renderQuestions(); renderBankPanel(); });
function applyLanguage(code) { const dictionary = translations[code] || translations.en; const languageField = document.getElementById('language'); if (languageField) languageField.value = code; document.querySelectorAll('[data-i18n]').forEach(function (element) { if (dictionary[element.dataset.i18n]) element.textContent = dictionary[element.dataset.i18n]; }); document.querySelectorAll('[data-welcome-index]').forEach(function (element) { const item = dictionary.welcome_items && dictionary.welcome_items[Number(element.dataset.welcomeIndex)]; if (item) element.lastChild.textContent = item; }); const loadingPanel = document.getElementById('loading-panel'); if (loadingPanel) loadingPanel.querySelector('span:last-child').textContent = dictionary.loading; }
document.getElementById('nav-language').addEventListener('change', function () { applyLanguage(this.value); document.querySelectorAll('.welcome-actions a').forEach(function (link) { const url = new URL(link.href); url.searchParams.set('language', this.value); link.href = url.toString(); }, this); });
const languageField = document.getElementById('language'); if (languageField) languageField.addEventListener('change', function () { document.getElementById('nav-language').value = this.value; applyLanguage(this.value); renderBankPanel(); });
const analysisForm = document.getElementById('analysis-form'); if (analysisForm) analysisForm.addEventListener('submit', function () { const button = document.getElementById('analyze-button'); button.disabled = true; button.querySelector('span').textContent = 'Preparing...'; document.getElementById('loading-panel').hidden = false; });
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
