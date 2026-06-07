# TODO

## Backlog

### Improvements
- Improve `_parse_time_input()` for better handling of edge cases and non-standard time formats.

### Architecture
- Allow multiple independent `Converter` instances by adding an optional `data_dir` parameter. This enables isolated configurations per instance (useful for testing, multiple projects, or advanced API usage).

## Future Ideas

- Add support for additional unit categories (e.g. currency, energy, fuel efficiency).
- Add internationalization / localized unit names and messages.

## Notes
- The project reached a stable v1.0.0 release.
- Most historical development tasks have been completed.
- This file is now focused only on remaining improvements and future directions.
