# Project Plan: rrweb Session Stitching and Consolidation

## Overview

This project processes session data captured via `rrweb`, which is stored as multiple JSON files in a Google Cloud Storage (GCS) bucket. Each file contains a partial recording of a session, identified by a shared `session_guid`. The objective is to:

1. Download all JSON files from the bucket.
2. Group files by `session_guid`.
3. Order each group by filename timestamp.
4. Validate and merge the `session_data` field into a complete rrweb recording.
5. Output a consolidated JSON file per session containing the full data and metadata.

## Input Format

Each JSON file contains:
- `session_guid`: a unique identifier for the session
- `session_data`: array of rrweb events
- `environment`: a string describing the environment (expected to be consistent within a session)

Filenames are formatted as timestamps and used for chronological ordering within a session.

## Output Format

Each session is written to a local file named `<session_guid>.json`, with the following structure:

```json
{
  "session_guid": "abc-123",
  "rrweb_data": [ /* combined rrweb events */ ],
  "metadata": {
    "environment": "production",
    "timestamp_list": [
      "2025-05-02T12:10:50.644423+0000",
      "2025-05-02T12:11:30.991832+0000",
      ...
    ]
  }
}
```

Each output file is saved in compact JSON format (no extra whitespace), stored locally under a filename matching the `session_guid` (e.g. `abc-123.json`).

## Processing Steps

1. **Initialize GCS Client**
   - Authenticate using `google-cloud-storage`.
   - List all `.json` files in the specified GCS bucket (flat structure, no subdirectories).

2. **Download & Parse Files**
   - Download each file.
   - Attempt to parse the content as JSON.
   - Validate that each file includes `session_guid`, `session_data`, and `environment`.
   - Log and skip files that are malformed or missing required fields.

3. **Group Files by `session_guid`**
   - Organize file contents into an in-memory dictionary grouped by `session_guid`.
   - Use the filename (timestamp-based) to preserve chronological order.

4. **Merge & Validate Session Data**
   - For each session:
     - Sort entries by filename-derived timestamp.
     - Concatenate all `session_data` arrays.
     - Collect a list of timestamps for metadata.
     - Deduplicate and verify the `environment` value:
       - If multiple values are encountered, log a warning and use the first one.

5. **Write Output Files**
   - Create a compact JSON object with the following structure:
     - `session_guid`: original session identifier.
     - `rrweb_data`: merged array of all rrweb events.
     - `metadata`:
       - `environment`: validated session environment.
       - `timestamp_list`: ordered list of all timestamps from source files.
   - Save the output to a local directory using `<session_guid>.json`.

6. **Logging**
   - Log counts for:
     - Total files processed.
     - Files skipped due to errors.
     - Sessions successfully written.
   - Log specific warnings for:
     - Malformed JSON files.
     - Inconsistent `environment` values within a session.

## Dependencies

- Python 3.8+
- `google-cloud-storage`
- `tqdm` (optional, for progress indicators)
- `logging` (built-in Python module)

## Notes

- The process is single-threaded for simplicity.
- Output directory will be created if it does not exist.
- All output files are compact (minified) JSON.
- The approach is scalable to modest data volumes (~600 MB total in current use case).
- Potential enhancements (for future iterations):
  - Parallel downloads and processing.
  - Upload consolidated sessions back to GCS.
  - Stream processing to reduce memory usage on large datasets.

## Example CLI Usage

```bash
python process_rrweb_sessions.py \
  --bucket rrweb-session-data \
  --output_dir ./stitched_sessions
```

