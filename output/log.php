<?php
/**
 * Performance Logging Endpoint
 *
 * Receives performance logs from the JavaScript PerformanceLogger
 * and stores them in daily JSONL files for later analysis.
 */

// Enable CORS for local development and production
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only accept POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Create logs directory if it doesn't exist
$logsDir = __DIR__ . '/logs';
if (!file_exists($logsDir)) {
    mkdir($logsDir, 0755, true);
}

// Create .htaccess to protect logs directory
$htaccessPath = $logsDir . '/.htaccess';
if (!file_exists($htaccessPath)) {
    file_put_contents($htaccessPath, "Deny from all\n");
}

// Get the log data
$rawInput = file_get_contents('php://input');
$data = json_decode($rawInput, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

// Validate required fields
if (!isset($data['sessionId']) || !isset($data['event'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields: sessionId, event']);
    exit;
}

// Add server-side timestamp and IP (for debugging)
$data['serverTimestamp'] = date('c');
$data['clientIP'] = $_SERVER['REMOTE_ADDR'] ?? 'unknown';

// Determine log file path (one file per day)
$logFile = $logsDir . '/perf_' . date('Y-m-d') . '.jsonl';

// Append log entry in JSONL format (one JSON object per line)
$success = file_put_contents($logFile, json_encode($data) . "\n", FILE_APPEND | LOCK_EX);

if ($success === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to write log']);
    exit;
}

// Return success
http_response_code(200);
echo json_encode([
    'status' => 'ok',
    'received' => 1
]);
