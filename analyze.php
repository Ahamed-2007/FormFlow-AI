<?php
declare(strict_types=1);
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/includes/ollama.php';
require_once __DIR__ . '/includes/services.php';
require_once __DIR__ . '/includes/official.php';
require_once __DIR__ . '/includes/translations.php';
require_once __DIR__ . '/includes/documents.php';
require_once __DIR__ . '/includes/banks.php';

$services = formFlowServices();
$officialSources = formFlowOfficialSources();
$banks = formFlowBanks();
$kycPurposes = formFlowKycPurposes();
$allowedLanguages = ['en', 'ta', 'hi', 'ml'];
$sessionState = $_SESSION['formflow'] ?? [];
$formType = trim((string) ($_POST['form_type'] ?? $sessionState['service_name'] ?? ''));
$language = formFlowLanguageCode(trim((string) ($_POST['language'] ?? $sessionState['language'] ?? 'en')));
$ui = formFlowTranslations()[$language];
$languageName = $ui['name'];
$question = trim((string) ($_POST['question'] ?? ''));
$answers = is_array($_POST['answers'] ?? null) ? $_POST['answers'] : [];
$history = [];
if (isset($_POST['history']) && is_string($_POST['history'])) {
    $decodedHistory = json_decode($_POST['history'], true);
    if (is_array($decodedHistory)) {
        foreach (array_slice(array_filter($decodedHistory, static fn ($item): bool => is_array($item)), -4) as $item) {
            $history[] = [
                'question' => substr((string) ($item['question'] ?? ''), 0, 400),
                'answer' => substr((string) ($item['answer'] ?? ''), 0, 1200),
            ];
        }
    }
}
$errorMessage = null;
$answer = '';
$service = null;
$checklist = [];
$readiness = ['percent' => 0, 'label' => 'NEEDS PREPARATION', 'tone' => 'red'];
$nextAction = 'Verify the current requirements with the relevant official authority.';
$official = null;
$isApplicationQuestion = false;
$selectedBank = null;
$kycPurpose = '';
$bankUiLabels = ['en'=>['bank'=>'Bank','purpose'=>'Purpose'],'ta'=>['bank'=>'வங்கி','purpose'=>'தேவை'],'hi'=>['bank'=>'बैंक','purpose'=>'आवश्यकता'],'ml'=>['bank'=>'ബാങ്ക്','purpose'=>'ആവശ്യം']];

if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['download'], $_SESSION['formflow']['guide'])) {
    $guide = $_SESSION['formflow']['guide'];
    if ($_GET['download'] === 'word') outputFormFlowWord($guide);
    if ($_GET['download'] === 'pdf') outputFormFlowPdf($guide);
}

function e(string $value): string { return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function ui(string $key): string { global $language; return t($key, $language); }
function translatedSuggestions(string $language, string $service, string $question): array
{
    if ($service === 'Bank KYC') {
        return [
            'en' => ['Can I do this online?', 'What documents should I prepare?', 'What happens after submission?', 'Do I need to visit a branch?', 'Do I need to renew this later?'],
            'ta' => ['இதை இணையத்தில் செய்ய முடியுமா?', 'என்ன ஆவணங்களைத் தயாரிக்க வேண்டும்?', 'சமர்ப்பித்த பிறகு என்ன நடக்கும்?', 'நான் கிளைக்குச் செல்ல வேண்டுமா?', 'இதை மீண்டும் புதுப்பிக்க வேண்டுமா?'],
            'hi' => ['क्या यह ऑनलाइन किया जा सकता है?', 'मुझे कौन से दस्तावेज़ तैयार करने चाहिए?', 'जमा करने के बाद क्या होगा?', 'क्या मुझे शाखा में जाना होगा?', 'क्या इसे बाद में नवीनीकृत करना होगा?'],
            'ml' => ['ഇത് ഓൺലൈനായി ചെയ്യാമോ?', 'ഏത് രേഖകളാണ് തയ്യാറാക്കേണ്ടത്?', 'സമർപ്പിച്ചതിന് ശേഷം എന്ത് സംഭവിക്കും?', 'ഞാൻ ശാഖയിൽ പോകണമോ?', 'ഇത് പിന്നീട് പുതുക്കണമോ?'],
        ][$language] ?? [];
    }
    $sets = [
        'en' => ['Show my personalized checklist', "I don't have one of these documents", 'What should I prepare first?', 'What happens after submission?', 'Where do I apply?'],
        'ta' => ['எனது தனிப்பயன் பட்டியலைக் காண்பிக்கவும்', 'என்னிடம் ஒரு ஆவணம் இல்லை', 'முதலில் நான் எதைத் தயாரிக்க வேண்டும்?', 'விண்ணப்பித்த பிறகு என்ன நடக்கும்?', 'நான் எங்கு விண்ணப்பிக்கலாம்?'],
        'hi' => ['मेरी व्यक्तिगत सूची दिखाएँ', 'मेरे पास एक दस्तावेज़ नहीं है', 'मुझे पहले क्या तैयार करना चाहिए?', 'आवेदन के बाद क्या होगा?', 'मैं कहाँ आवेदन कर सकता हूँ?'],
        'ml' => ['എന്റെ വ്യക്തിഗത പട്ടിക കാണിക്കുക', 'എന്റെ പക്കൽ ഒരു രേഖയില്ല', 'ആദ്യം ഞാൻ എന്ത് തയ്യാറാക്കണം?', 'അപേക്ഷിച്ചതിന് ശേഷം എന്ത് സംഭവിക്കും?', 'എവിടെയാണ് അപേക്ഷിക്കേണ്ടത്?'],
    ];
    return $sets[$language] ?? $sets['en'];
}
function answerStatus(array $item, array $answers): string
{
    if (($item['status'] ?? '') === 'verify') return 'verify';
    $value = (string) ($answers[$item['question'] ?? ''] ?? '');
    return $value === 'yes' ? 'ready' : ($value === 'no' ? 'prepare' : 'verify');
}
function statusLabel(string $status): string { global $language; return ['ready' => t('available', $language), 'prepare' => t('prepare_status', $language), 'verify' => t('conditional', $language)][$status] ?? t('conditional', $language); }
function statusIcon(string $status): string { return ['ready' => '✓', 'prepare' => '!', 'verify' => '?'][$status] ?? '?'; }
function isApplicationQuestion(string $question): bool
{
    $question = strtolower($question);
    foreach (['where can i apply', 'how do i apply', 'application website', 'official website', 'where should i submit', 'apply online', 'online application', 'application portal', 'where do i apply'] as $phrase) {
        if (str_contains($question, $phrase)) return true;
    }
    return false;
}
function renderOfficialCard(?array $official, string $service, bool $showLink): string
{
    $html = '<section class="official-card mt-4"><div class="official-heading"><span class="official-emblem">&#127963;</span><div><p class="section-kicker mb-1">' . e(ui('official')) . '</p><h3>' . e($official['authority'] ?? 'Relevant official authority') . '</h3></div>';
    if (($official['verified'] ?? false) === true) $html .= '<span class="official-badge">&#10003; ' . e(ui('source')) . '</span>';
    $html .= '</div><p class="official-source">' . e(ui('source_label')) . ': ' . e($official['source_label'] ?? ui('unavailable')) . '</p>';
    if (!empty($official['last_verified_date'])) $html .= '<p class="official-verified">' . e(ui('verified')) . ': ' . e($official['last_verified_date']) . '</p>';
    if ($showLink && ($official['verified'] ?? false) === true && !empty($official['application_url'])) {
        $html .= '<a class="official-action" href="' . e($official['application_url']) . '" target="_blank" rel="noopener noreferrer">&#128279; ' . e(ui('open')) . ' <span>&#8599;</span></a>';
        if (!empty($official['information_url'])) $html .= '<a class="official-info" href="' . e($official['information_url']) . '" target="_blank" rel="noopener noreferrer">&#8505; ' . e(ui('info')) . '</a>';
    } else {
        $html .= '<div class="official-unverified">' . e(ui('unavailable')) . '</div>';
    }
    $html .= '<p class="official-note">' . e(ui('official_note')) . '</p></section>';
    return $html;
}
function followUpSuggestions(string $service, string $question): array
{
    $question = strtolower($question);
    if (str_contains($question, 'document') || str_contains($question, 'missing')) {
        $suggestions = ['Show my personalized checklist', "I don't have one of these documents", 'What should I prepare first?'];
    } elseif (str_contains($question, 'submit') || str_contains($question, 'after')) {
        $suggestions = ['What happens after submission?', 'Is there another step after this?', 'How might verification work?'];
    } else {
        $suggestions = ['Show my personalized checklist', 'What document am I missing?', 'What should I do next?'];
    }
    if (str_contains($service, 'Licence')) {
        $suggestions[] = 'What should I prepare for the test?';
    } elseif ($service === 'Scholarship Application') {
        $suggestions[] = 'What should I check before submitting?';
    } elseif ($service === 'Bank KYC') {
        $suggestions[] = 'Do I need to renew this later?';
    } else {
        $suggestions[] = 'What happens after submission?';
    }
    $suggestions[] = 'Where do I apply?';
    return array_values(array_unique($suggestions));
}
function followUpFallback(string $service, string $question, string $nextAction): string
{
    $question = strtolower($question);
    if (isApplicationQuestion($question)) {
        return "## Where can you apply?\nThe controlled official application card below shows the verified portal when one is available for this service. Use it to check the current requirements and application process before submitting.\n\n## What to do next\nOpen the official application card below, confirm that it applies to your authority or jurisdiction, and then review your preparation checklist.";
    }
    if (str_contains($question, 'after') || str_contains($question, 'submit')) {
        return "## Answer\nAfter submission, the relevant authority, provider, or bank may review the information and supporting details. The exact verification steps, processing time, notifications, and outcome depend on the service and local authority.\n\n## What to do next\nKeep your submission reference or confirmation if one is provided, monitor the official channel, and verify any request for additional information.\n\n## Important note\nRequirements and processing details may vary. Verify the current process with the relevant official authority.";
    }
    if (str_contains($question, 'checklist') || str_contains($question, 'missing') || str_contains($question, 'document')) {
        return "## Answer\nYour checklist separates items you marked as ready from items that need preparation or official verification. A missing item does not automatically prove that a specific alternative will be accepted.\n\n## What to do next\nStart with the first item marked NEED TO PREPARE, or verify the first item marked CONDITIONAL / VERIFY.\n\n## Important note\nAccepted documents and alternatives may vary for {$service}. Verify them with the relevant official authority.";
    }
    return "## Answer\nYour readiness estimate is based only on the information you provided. Use the checklist and journey stages to organize your preparation for {$service}.\n\n## What to do next\n{$nextAction}\n\n## Important note\nVerify current requirements with the relevant official authority.";
}
function renderAnswer(string $answer): string
{
    $html = '';
    $open = false;
    $list = false;
    foreach (preg_split('/\R/', trim($answer)) ?: [] as $line) {
        $line = trim($line);
        if ($line === '') { if ($list) { $html .= '</ul>'; $list = false; } continue; }
        if (str_starts_with($line, '## ')) {
            if ($list) { $html .= '</ul>'; $list = false; }
            if ($open) $html .= '</div></article>';
            $html .= '<article class="answer-section"><h3>' . e(trim(substr($line, 3))) . '</h3><div class="answer-content">';
            $open = true;
        } elseif (preg_match('/^(?:[-*]|\d+[.)])\s+(.+)$/', $line, $match)) {
            if (!$list) { $html .= '<ul class="answer-list">'; $list = true; }
            $html .= '<li>' . e($match[1]) . '</li>';
        } else {
            if ($list) { $html .= '</ul>'; $list = false; }
            if (!$open) { $html .= '<article class="answer-section"><div class="answer-content">'; $open = true; }
            $html .= '<p>' . e($line) . '</p>';
        }
    }
    if ($list) $html .= '</ul>';
    if ($open) $html .= '</div></article>';
    return $html ?: '<p>No AI explanation was returned.</p>';
}

try {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') throw new InvalidArgumentException(t('answer', $language));
    if (!isset($services[$formType])) throw new InvalidArgumentException(t('choose', $language));
    if (!in_array($language, ['en', 'ta', 'hi', 'ml'], true)) throw new InvalidArgumentException(t('language', $language));
    if ($question === '') throw new InvalidArgumentException(t('question', $language));
    if (strlen($question) > 8000) throw new InvalidArgumentException('Please keep your question under 2,000 characters.');
    $service = $services[$formType];
    if ($formType === 'Bank KYC') {
        $bankId = trim((string) ($answers['bank_id'] ?? ''));
        if (!isset($banks[$bankId])) throw new InvalidArgumentException('Please select a bank for Bank KYC.');
        $selectedBank = $banks[$bankId];
        $kycPurpose = (string) ($answers['kyc_purpose'] ?? '');
        if (!isset($kycPurposes[$kycPurpose])) throw new InvalidArgumentException('Please select what you need for Bank KYC.');
        $official = ['authority'=>$selectedBank['bank_name'], 'application_url'=>$selectedBank['url'], 'information_url'=>$selectedBank['url'], 'source_label'=>$selectedBank['source'], 'verified'=>$selectedBank['verified'], 'last_verified_date'=>'2026-09-04', 'scope_note'=>'Use the selected bank’s official channel. KYC availability and process may vary by purpose and bank.'];
    } else {
        $official = $officialSources[$formType] ?? null;
    }
    $isApplicationQuestion = isApplicationQuestion($question);

    $_SESSION['formflow'] = [
        'service_id' => strtolower(str_replace(' ', '_', $formType)),
        'service_name' => $formType,
        'language' => $language,
        'intake' => $answers,
        'original_question' => $_SESSION['formflow']['original_question'] ?? $question,
        'conversation' => $history,
        'journey_stage' => $_SESSION['formflow']['journey_stage'] ?? 'Understand',
        'official_application_url' => $official['application_url'] ?? null,
        'official_information_url' => $official['information_url'] ?? null,
        'authority' => $official['authority'] ?? null,
        'source_name' => $official['source_label'] ?? null,
        'verification_status' => (bool) ($official['verified'] ?? false),
        'last_verified_date' => $official['last_verified_date'] ?? null,
        'selected_bank' => $selectedBank['id'] ?? null,
        'selected_bank_name' => $selectedBank['bank_name'] ?? null,
        'kyc_purpose' => $kycPurpose,
    ];

    foreach ($service['checklist'] as $item) {
        $status = answerStatus($item, $answers);
        $checklist[] = ['label' => $item['label'], 'status' => $status];
    }
    $readyCount = count(array_filter($checklist, static fn (array $item): bool => $item['status'] === 'ready'));
    $prepareCount = count(array_filter($checklist, static fn (array $item): bool => $item['status'] === 'prepare'));
    $readiness['percent'] = (int) round(($readyCount / max(count($checklist), 1)) * 100);
    if ($prepareCount === 0 && $readiness['percent'] >= 70) { $readiness['label'] = t('ready_status', $language); $readiness['tone'] = 'green'; }
    elseif ($readiness['percent'] >= 40) { $readiness['label'] = t('almost', $language); $readiness['tone'] = 'yellow'; }
    else { $readiness['label'] = t('needs', $language); }
    foreach ($checklist as $item) {
        if ($item['status'] === 'prepare') { $nextAction = t('prepare_status', $language) . ': ' . $item['label']; break; }
        if ($item['status'] === 'verify') { $nextAction = t('conditional', $language) . ': ' . $item['label']; }
    }

    $answerContext = json_encode(['answers' => $answers, 'checklist' => $checklist, 'readiness_estimate' => $readiness['label'], 'bank' => $selectedBank['bank_name'] ?? null, 'kyc_purpose' => $kycPurposes[$kycPurpose] ?? null], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $historyContext = $history === [] ? 'No earlier follow-up questions.' : json_encode($history, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    $isFollowUp = $history !== [];
    $responseInstructions = $isFollowUp
        ? "Answer this follow-up directly in {$languageName} using short paragraphs and at most 3 bullet points. Start with ## Answer, then use ## What to do next. Do not repeat the entire readiness report."
        : "Write the entire answer in {$languageName}. Use exactly these headings, each beginning with ##: ## Readiness summary ## Prepare before you apply ## What happens next? ## Future steps ## Your next action.";
    $directAnswerInstruction = $isApplicationQuestion
        ? "Answer the user's application-location question first and clearly. Do not invent or output a URL; the PHP application supplies the official link card separately."
        : 'Answer the user’s specific question first, then connect it to their preparation context.';
    $prompt = <<<PROMPT
You are FormFlow AI, an Application Readiness and Journey Navigator.
Service: {$formType}
User language: {$languageName}
User question: {$question}
User intake and preparation estimate: {$answerContext}
Previous conversation context: {$historyContext}

{$responseInstructions}
$directAnswerInstruction

Explain the user's personalized situation from the intake. Be concise and practical. Mention missing or conditional items without claiming they are legally mandatory. Do not invent official requirements, eligibility, fees, deadlines, processing times, bank policies, test rules, alternatives, or URLs. Mark uncertain items as conditional and say: requirements may vary; verify current requirements with the relevant official authority, bank, provider, or state. For times, say only officially stated, estimated/may vary, or not confirmed when appropriate. Give exactly one immediate next action.
PROMPT;
    try {
        $answer = generateOllamaResponse($prompt, $isFollowUp ? 90 : 700, $isFollowUp ? 35 : OLLAMA_REQUEST_TIMEOUT);
    } catch (Throwable $generationError) {
        if (!$isFollowUp && !$isApplicationQuestion) throw $generationError;
        $answer = followUpFallback($formType, $question, $nextAction);
    }
    $history[] = ['question' => $question, 'answer' => $answer];
    $history = array_slice($history, -6);
    $_SESSION['formflow']['conversation'] = $history;
    $_SESSION['formflow']['journey_stage'] = $isApplicationQuestion ? 'Apply' : ($_SESSION['formflow']['journey_stage'] ?? 'Understand');
    $guideName = $formType === 'Bank KYC' && $selectedBank ? $selectedBank['bank_name'] . ' — KYC' : $formType;
    $_SESSION['formflow']['guide'] = formFlowGuideData($guideName, $language, $checklist, $readiness['label'], $answer, $nextAction, $official ?? [], $service['journey']);
} catch (InvalidArgumentException $error) {
    http_response_code(400);
    $errorMessage = $error->getMessage();
} catch (Throwable $error) {
    http_response_code(502);
    $errorMessage = $error->getMessage();
}
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Readiness Dashboard | FormFlow AI</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"><link rel="stylesheet" href="css/style.css">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark app-nav"><div class="container py-2"><a class="navbar-brand fw-bold" href="index.php"><span class="brand-mark">F</span> FormFlow AI</a><button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#appNav" aria-controls="appNav" aria-expanded="false" aria-label="Toggle navigation"><span class="navbar-toggler-icon"></span></button><div class="collapse navbar-collapse" id="appNav"><ul class="navbar-nav ms-auto align-items-lg-center gap-lg-2"><li class="nav-item"><a class="nav-link" href="index.php"><?= e(ui('home')) ?></a></li><li class="nav-item"><a class="nav-link" href="#journey"><?= e(ui('journey')) ?></a></li><li class="nav-item"><a class="nav-link" href="index.php#how-it-works"><?= e(ui('how')) ?></a></li><li class="nav-item"><a class="nav-link" href="index.php#about"><?= e(ui('about')) ?></a></li><li class="nav-item"><label class="visually-hidden" for="result-language">Language</label><select id="result-language" class="nav-language-select" aria-label="<?= e(ui('language_label')) ?>"><?php foreach (formFlowTranslations() as $optionCode => $optionDictionary): ?><option value="<?= e($optionCode) ?>"<?= $optionCode === $language ? ' selected' : '' ?>><?= e($optionDictionary['name']) ?></option><?php endforeach; ?></select></li></ul></div></div></nav>
<main class="result-page container py-5">
<?php if ($errorMessage !== null): ?>
    <div class="result-toolbar d-flex justify-content-between align-items-center gap-3 mb-4"><div><p class="section-kicker mb-1">FormFlow</p><h1 class="h2 mb-0"><?= e(ui('answer')) ?></h1></div><a href="index.php" class="btn btn-primary"><?= e(ui('new')) ?></a></div><div class="alert error-panel"><h2 class="h4"><?= e(ui('answer')) ?></h2><p class="mb-0"><?= e($errorMessage) ?></p></div>
<?php else: ?>
    <div class="result-toolbar d-flex flex-wrap justify-content-between align-items-center gap-3 mb-4"><div><p class="section-kicker mb-1"><?= e(ui('journey')) ?></p><h1 class="h2 mb-0"><?= e($formType) ?></h1></div><div class="d-flex gap-2"><a href="index.php" class="btn btn-outline-secondary"><?= e(ui('home')) ?></a><a href="index.php?reset=1" class="btn btn-primary"><?= e(ui('new')) ?></a></div></div>
    <div class="result-meta mb-4"><span><strong><?= e(ui('service')) ?></strong> <?= e($formType) ?></span><?php if ($formType === 'Bank KYC' && $selectedBank): ?><span><strong><?= e($bankUiLabels[$language]['bank']) ?></strong> <?= e($selectedBank['bank_name']) ?></span><span><strong><?= e($bankUiLabels[$language]['purpose']) ?></strong> <?= e($kycPurposes[$kycPurpose]) ?></span><?php endif; ?><span><strong><?= e(ui('language_label')) ?></strong> <?= e($languageName) ?></span><span><strong><?= e(ui('category')) ?></strong> <?= e($service['category']) ?></span></div>
    <div class="row g-4" id="journey"><div class="col-lg-8">
    <div class="row g-4 mb-4"><div class="col-lg-5"><section class="dashboard-card readiness-card tone-<?= e($readiness['tone']) ?>"><p class="section-kicker mb-2">BASED ON YOUR ANSWERS</p><div class="readiness-top"><div><h2><?= e($readiness['label']) ?></h2><p>FormFlow preparation estimate</p></div><strong class="readiness-number"><?= $readiness['percent'] ?>%</strong></div><div class="progress readiness-progress"><div class="progress-bar" style="width: <?= $readiness['percent'] ?>%"></div></div><small>This is not an official government, bank, or provider score.</small></section></div><div class="col-lg-7"><section class="dashboard-card"><div class="card-heading"><div><p class="section-kicker mb-1">PREPARATION SNAPSHOT</p><h2>What your answers show</h2></div><span class="service-badge"><?= e($service['category']) ?></span></div><div class="status-summary"><?php foreach (['ready' => 'Ready', 'prepare' => 'Prepare', 'verify' => 'Verify'] as $status => $label): ?><span class="status-pill status-<?= e($status) ?>"><?= statusIcon($status) ?> <?= $label ?> <?= count(array_filter($checklist, static fn (array $item): bool => $item['status'] === $status)) ?></span><?php endforeach; ?></div><p class="card-copy mb-0">Your checklist separates what you marked as available from items that need preparation or official verification.</p></section></div></div>
    <div class="row g-4"><div class="col-lg-5"><section class="dashboard-card h-100"><div class="card-heading"><div><p class="section-kicker mb-1">MY APPLICATION CHECKLIST</p><h2>Prepare with confidence</h2></div></div><?php foreach ($checklist as $item): ?><div class="checklist-row status-<?= e($item['status']) ?>"><span class="check-icon"><?= statusIcon($item['status']) ?></span><div><strong><?= e($item['label']) ?></strong><small><?= e(statusLabel($item['status'])) ?></small></div></div><?php endforeach; ?><div class="missing-callout mt-4"><strong>Don’t have an item?</strong><br><span>Accepted alternatives may vary. Verify what can satisfy it with the relevant authority.</span></div></section></div><div class="col-lg-7"><section class="dashboard-card journey-card"><div class="card-heading"><div><p class="section-kicker mb-1">APPLICATION JOURNEY</p><h2>From prepare to next step</h2></div></div><div class="timeline"><?php foreach ($service['journey'] as $index => $stage): ?><div class="timeline-step"><span><?= $index + 1 ?></span><div><strong><?= e($stage) ?></strong><small><?= $index === 0 ? 'Start with the information and items you can prepare.' : 'Details and timing may vary. Verify with the relevant authority.' ?></small></div></div><?php endforeach; ?></div></section></div></div>
    <section class="dashboard-card ai-card mt-4"><div class="card-heading"><div><p class="section-kicker mb-1"><?= e(ui('answer')) ?></p><h2><?= e(ui('how_title')) ?></h2></div></div><div class="question-quote"><span><?= e(ui('answer_context')) ?></span><?= e($question) ?></div><div class="answer-content"><?= renderAnswer($answer) ?></div><?= renderOfficialCard($official, $formType, true) ?></section>
    <?php $guide = $_SESSION['formflow']['guide'] ?? formFlowGuideData($formType, $language, $checklist, $readiness['label'], $answer, $nextAction, $official ?? [], $service['journey']); ?>
    <section class="dashboard-card guidance-card mt-4"><div class="row g-4"><div class="col-md-6"><h3><?= e($guide['labels']['what_do']) ?></h3><ul class="guide-list do-list"><?php foreach ($guide['do'] as $item): ?><li><?= e($item) ?></li><?php endforeach; ?></ul></div><div class="col-md-6"><h3><?= e($guide['labels']['what_not']) ?></h3><ul class="guide-list dont-list"><?php foreach ($guide['dont'] as $item): ?><li><?= e($item) ?></li><?php endforeach; ?></ul></div></div></section>
    <section class="dashboard-card download-card mt-4"><p class="section-kicker mb-1"><?= e($guide['labels']['title']) ?></p><h2><?= e($guide['labels']['title']) ?></h2><p><?= e($guide['labels']['description']) ?></p><div class="download-actions"><a class="btn btn-primary" href="analyze.php?download=pdf" target="_blank" rel="noopener noreferrer">&#128196; <?= e($guide['labels']['pdf']) ?></a><a class="btn btn-outline-primary" href="analyze.php?download=word" target="_blank" rel="noopener noreferrer">&#128221; <?= e($guide['labels']['word']) ?></a></div></section>
    <section class="dashboard-card next-action-card mt-4"><p class="section-kicker mb-1"><?= e(ui('keep')) ?></p><h2><?= e(ui('next_action')) ?></h2><p><?= e($nextAction) ?></p><a href="index.php?reset=1" class="btn btn-primary"><?= e(ui('new_action')) ?></a></section>
    </div><aside class="col-lg-4"><div class="assistant-card"><div class="assistant-head"><span class="assistant-icon">&#129302;</span><div><strong>FormFlow AI</strong><small><?= e(ui('journey')) ?></small></div></div><p class="assistant-prompt"><?= e(ui('next_question')) ?></p><div class="suggestion-list"><?php foreach (translatedSuggestions($language, $formType, $question) as $suggestion): ?><form action="analyze.php" method="POST"><input type="hidden" name="form_type" value="<?= e($formType) ?>"><input type="hidden" name="language" value="<?= e($language) ?>"><input type="hidden" name="question" value="<?= e($suggestion) ?>"><input type="hidden" name="history" value="<?= e(json_encode($history, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) ?>"><?php foreach ($answers as $key => $value): ?><input type="hidden" name="answers[<?= e((string) $key) ?>]" value="<?= e((string) $value) ?>"><?php endforeach; ?><button class="suggestion-button" type="submit"><span><?= e($suggestion) ?></span><b>&#8599;</b></button></form><?php endforeach; ?></div><div class="assistant-divider"></div><form action="analyze.php" method="POST" class="assistant-input"><input type="hidden" name="form_type" value="<?= e($formType) ?>"><input type="hidden" name="language" value="<?= e($language) ?>"><input type="hidden" name="history" value="<?= e(json_encode($history, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES)) ?>"><?php foreach ($answers as $key => $value): ?><input type="hidden" name="answers[<?= e((string) $key) ?>]" value="<?= e((string) $value) ?>"><?php endforeach; ?><label for="follow-up-question"><?= e(ui('ask')) ?></label><textarea id="follow-up-question" name="question" rows="3" placeholder="<?= e(ui('ask')) ?>" required></textarea><button class="btn btn-primary w-100" type="submit"><?= e(ui('send')) ?> <span>&#8594;</span></button></form></div></aside></div>
<?php endif; ?>
</main><footer class="text-center py-4"><small><?= e(ui('footer')) ?></small></footer><script>document.getElementById('result-language').addEventListener('change', function () { document.querySelectorAll('input[name="language"]').forEach(function (input) { input.value = this.value; }, this); }); document.querySelectorAll('.assistant-card form').forEach(function (form) { form.addEventListener('submit', function () { form.classList.add('is-asking'); const button = form.querySelector('button[type="submit"]'); if (button) { button.disabled = true; button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span> Asking...'; } }); });</script><script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body></html>
