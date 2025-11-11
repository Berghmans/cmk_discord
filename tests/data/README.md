# Test Data for CheckMK Discord Notifications

This directory contains test data files for different CheckMK versions.

## Directory Structure

```
data/
├── 2.2.0p21/           # CheckMK version 2.2.0p21
│   ├── service/        # Service notification test cases
│   └── host/           # Host notification test cases
└── [future versions]/  # Add new versions as needed
```

## JSON File Format

Each JSON file represents the raw environment variables as they would be passed from CheckMK to the notification script.

**Important:** The keys in the JSON files **MUST** have the `NOTIFY_` prefix, exactly as CheckMK passes them. The test data loader (`load_test_data()`) will automatically strip the prefix when loading, simulating what `Context.from_env()` does in the actual script.

### Example Service Notification

```json
{
  "NOTIFY_WHAT": "SERVICE",
  "NOTIFY_NOTIFICATIONTYPE": "PROBLEM",
  "NOTIFY_HOSTNAME": "webserver01",
  "NOTIFY_SERVICEDESC": "HTTP",
  "NOTIFY_SERVICESTATE": "CRITICAL",
  "NOTIFY_LASTSERVICESTATE": "OK",
  "NOTIFY_SERVICEOUTPUT": "Connection timeout",
  "NOTIFY_SERVICECHECKCOMMAND": "check_http",
  "NOTIFY_SERVICEURL": "/check_mk/view.py?host=webserver01&service=HTTP",
  "NOTIFY_SHORTDATETIME": "2025-01-15T10:30:00",
  "NOTIFY_OMD_SITE": "production",
  "NOTIFY_PARAMETER_1": "https://discord.com/api/webhooks/...",
  "NOTIFY_PARAMETER_2": "https://checkmkhost.mycompany.com/my_monitoring"
}
```

### Example Host Notification

```json
{
  "NOTIFY_WHAT": "HOST",
  "NOTIFY_NOTIFICATIONTYPE": "PROBLEM",
  "NOTIFY_HOSTNAME": "webserver01",
  "NOTIFY_HOSTSTATE": "DOWN",
  "NOTIFY_PREVIOUSHOSTHARDSTATE": "UP",
  "NOTIFY_HOSTOUTPUT": "Host Unreachable",
  "NOTIFY_HOSTCHECKCOMMAND": "check-host-alive",
  "NOTIFY_HOSTURL": "/check_mk/view.py?host=webserver01",
  "NOTIFY_SHORTDATETIME": "2025-01-15T10:30:00",
  "NOTIFY_OMD_SITE": "production",
  "NOTIFY_PARAMETER_1": "https://discord.com/api/webhooks/...",
  "NOTIFY_PARAMETER_2": "https://checkmkhost.mycompany.com/my_monitoring"
}
```

## Adding New Test Cases

1. Create a new JSON file in the appropriate version/type directory
2. Use descriptive filenames (e.g., `problem_critical.json`, `recovery_ok.json`)
3. Include all required fields for the notification type
4. Optional fields like `NOTIFICATIONCOMMENT` can be added as needed

## Adding New CheckMK Versions

When a new CheckMK version introduces format changes:

1. Create a new version directory (e.g., `2.3.0/`)
2. Add `service/` and `host/` subdirectories
3. Create test cases reflecting the new format
4. Update tests to handle both versions

## Test Data Scenarios

### Service Notifications
- `problem_critical.json` - Service going from OK to CRITICAL
- `problem_warning.json` - Service going from OK to WARNING
- `recovery_ok.json` - Service recovering from CRITICAL to OK
- `acknowledgement.json` - Service acknowledgement with comment

### Host Notifications
- `problem_down.json` - Host going DOWN
- `recovery_up.json` - Host recovering to UP
- `unreachable.json` - Host becoming UNREACHABLE
- `downtime_start.json` - Scheduled downtime with comment
