<?php

declare(strict_types=1);

if (session_status() !== PHP_SESSION_ACTIVE) {
	session_start();
}

header('Content-Type: text/html; charset=UTF-8');

error_reporting(E_ALL);
ini_set('display_errors', '0');
ini_set('display_startup_errors', '0');

const OLLAMA_URL = 'http://localhost:11434/api/generate';
const OLLAMA_HOST = 'http://127.0.0.1:11434';
const OLLAMA_MODEL = 'llama3.2:3b';
const OLLAMA_CONNECT_TIMEOUT = 5;
const OLLAMA_REQUEST_TIMEOUT = 120;

set_exception_handler(static function (Throwable $error): void {
	http_response_code(500);
	echo '<!doctype html><html lang="en"><head><meta charset="UTF-8"><title>FormFlow AI Error</title></head><body><main style="max-width:680px;margin:4rem auto;font-family:Arial,sans-serif"><h1>FormFlow AI could not complete that request</h1><p>Please return to the home page and try again.</p><p><a href="index.php">Back to FormFlow AI</a></p></main></body></html>';
});
