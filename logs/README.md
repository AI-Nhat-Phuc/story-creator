# Logs Directory

This directory contains application log files.

## Log Files

Log files are created daily with the format:
- `story_creator_YYYYMMDD.log`

## Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

## Configuration

Logging is configured in `utils/logging_config.py`.

To change log level or disable file logging, modify `main.py`:

```python
setup_logging(
    log_level=logging.DEBUG,  # Change to DEBUG, INFO, WARNING, ERROR
    log_to_file=True,          # Set to False to disable file logging
    log_dir="logs"             # Change log directory
)
```

## Log Rotation

Logs are rotated daily. Old log files are kept for reference.
Consider setting up log rotation or cleanup for production use.
