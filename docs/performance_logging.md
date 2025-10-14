# Performance Logging System

Centralized performance monitoring for rennie.org to diagnose timing issues and UX problems.

## Overview

The system consists of three components:
1. **JavaScript Logger** (`PerformanceLogger` in `app.js`) - Tracks events client-side
2. **PHP Endpoint** (`log.php`) - Receives logs on the server
3. **Python Analyzer** (`scripts/analyze_logs.py`) - Downloads and analyzes logs

## How It Works

1. **Client**: User visits rennie.org → JavaScript logs events → Batches sent to server
2. **Server**: PHP receives logs → Stores in daily JSONL files → Protected by .htaccess
3. **Analysis**: Python downloads logs → Parses and analyzes → Generates reports

## Events Tracked

### Page Load
- `page_load_metrics` - DNS, TCP, request/response times, transfer size

### App Lifecycle
- `app_init_start` → `app_init_complete`
- `content_fetch_start` → `content_fetch_complete`
- `app_listeners_setup`

### Images
- `carousel_initial_image_start` → `carousel_initial_image_loaded`
- `single_image_load_start` → `single_image_loaded`
- `carousel_image_preloaded` / `carousel_image_cache_hit`

### Transitions
- `carousel_transition_start` → `carousel_transition_complete`
- `quote_transition_start` → `quote_transition_complete`
- `carousel_fade_started`
- `quote_fade_in_start` → `quote_fade_in_complete`

### Color Analysis
- `color_analysis_start` → `color_analysis_complete`

## Log Format

Each log entry is a JSON object with:
```json
{
  "sessionId": "session_1728928060_abc123",
  "timestamp": "2025-10-14T12:27:40.123Z",
  "relativeTime": 145,
  "event": "carousel_initial_image_loaded",
  "cacheStatus": "network",
  "path": "images/pmarca-pmf_v1.png",
  "duration": 234,
  "serverTimestamp": "2025-10-14T12:27:40+00:00",
  "clientIP": "192.168.1.1"
}
```

## Usage

### Viewing Logs in Browser Console

The logger outputs color-coded logs automatically:
- 🔵 Blue: start events
- 🟢 Green: complete/success events
- 🔴 Red: errors
- 🟣 Purple: transitions

```javascript
// View statistics
perfLogger.getStats()

// View raw events
perfLogger.events

// Export to JSON file
perfLogger.exportLogs()

// Disable logging
perfLogger.enabled = false

// Disable server logging (localStorage only)
perfLogger.serverLoggingEnabled = false
```

### Analyzing Logs

```bash
# Analyze today's logs (downloads from server)
python scripts/analyze_logs.py

# Analyze specific date
python scripts/analyze_logs.py --date 2025-10-13

# Analyze local logs only (skip download)
python scripts/analyze_logs.py --local-only
```

### Manual Log Download

Logs are stored on the server at:
```
rennie.org/logs/perf_YYYY-MM-DD.jsonl
```

To download manually:
```bash
scp rennieorg@rennie.org:~/rennie.org/logs/perf_2025-10-14.jsonl logs/
```

Note: The logs directory is protected by .htaccess to prevent web access.

## Analysis Output

The analyzer provides:
- **Session count** and grouping (cached vs network loads)
- **Average timings** for app init, image loads
- **Session details** with full metrics
- **Slow session detection** (>500ms image loads)

Example output:
```
📊 PERFORMANCE LOG ANALYSIS
================================================================================

Total Sessions: 5

🔵 NETWORK LOADS (First-time visitors)
   Sessions: 2
   Avg App Init: 234ms
   Avg Image Load: 345ms

🟢 CACHED LOADS (Returning visitors)
   Sessions: 3
   Avg App Init: 89ms
   Avg Image Load: 12ms

────────────────────────────────────────────────────────────────────────────────
📋 SESSION DETAILS

🔵 Session 1: session_1728928060...
   Status: network
   Duration: 5234ms
   App Init: 234ms
   Images Loaded: 3
   Image Load Times: avg=345ms, max=456ms, min=234ms
   Transitions: 2 carousel, 1 quotes
```

## Configuration

### Batching
Logs are batched to reduce HTTP requests:
- **Batch size**: 5 events
- **Batch delay**: 2 seconds after last event
- **Flush on**: page unload, tab switch

### Endpoints
- **Local**: `http://localhost:8000/log.php`
- **Production**: `https://rennie.org/log.php`

Auto-detected based on hostname.

## Troubleshooting

### Logs not appearing on server
1. Check console for errors: `Failed to send log to server`
2. Verify PHP endpoint is accessible: `curl https://rennie.org/log.php`
3. Check server logs directory exists: `ssh rennieorg@rennie.org "ls -la ~/rennie.org/logs"`

### Download fails
1. Verify SSH access: `ssh rennieorg@rennie.org`
2. Check log file exists: `ls -la logs/perf_*.jsonl`
3. Manually download via scp (see above)

### No events logged
1. Check if logging is enabled: `perfLogger.enabled`
2. Check browser console for JavaScript errors
3. Verify page loads correctly

## Disabling Logging

To disable logging entirely, edit `scripts/templates/app.js`:
```javascript
this.enabled = false;  // Disable all logging
```

Or just server logging:
```javascript
this.serverLoggingEnabled = false;  // localStorage only
```

## Log Management & Cleanup

### Automatic Cleanup
The PHP endpoint automatically deletes logs older than 90 days:
- Runs on 1% of requests (low overhead)
- No manual intervention needed
- Keeps storage under 6MB

### Daily File Size Limit
Each day's log file has a 10MB limit:
- Prevents abuse or runaway logging
- Returns HTTP 507 if limit reached
- Typical usage: ~67KB/day (149x under limit)

### Manual Cleanup
If needed, you can manually clean up logs:
```bash
# Preview what would be deleted (safe)
python scripts/cleanup_old_logs.py --dry-run

# Delete logs older than 90 days
python scripts/cleanup_old_logs.py

# Delete logs older than 30 days
python scripts/cleanup_old_logs.py --days 30
```

## Privacy & Data

- **Session IDs**: Randomly generated, stored in sessionStorage (cleared on browser close)
- **IP addresses**: Logged server-side for debugging, not shared
- **Personal data**: None collected - only timing and performance metrics
- **Retention**: Auto-deleted after 90 days, max 10MB per day

## File Locations

```
/output/log.php              # Server endpoint
/output/logs/                # Log storage (created automatically)
/output/logs/.htaccess       # Access protection
/scripts/analyze_logs.py     # Analysis tool
/scripts/templates/app.js    # PerformanceLogger class
/logs/                       # Downloaded logs (local)
```
