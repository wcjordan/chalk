# Session Stitching Project Todo List

## Step 1: List and Download JSON Files from GCS

### Tasks:
- [x] Install and import `google-cloud-storage` library
- [x] Create function to initialize GCS client using Application Default Credentials
- [x] Implement function to list all `.json` files in specified bucket (flat structure only)
- [x] Add function to download file contents into memory as bytes/strings
- [x] Return list of `(filename, file_content)` pairs
- [x] Add basic error handling for connection and file read errors
- [x] Add logging for operations and errors
- [x] Create main function demonstrating usage with `example-bucket`
- [x] Add verification: print number of JSON files found
- [x] Add verification: print first 100 characters of first file content
- [x] Write unit tests using mocks for GCS interaction

## Step 2: Parse and Validate a Single JSON File

### Tasks:
- [x] Create function to parse JSON content from file data
- [x] Add validation for required fields: `session_guid`, `session_data`, `environment`
- [x] Handle malformed JSON gracefully with try/catch
- [x] Handle missing required fields with appropriate error messages
- [x] Add logging for validation failures
- [x] Create test files: valid JSON, missing fields, corrupt format
- [x] Test parsing function on each test file type
- [x] Verify error handling works as expected
- [x] Write unit tests for edge cases (empty files, wrong data types, etc.)

## Step 3: Group Valid Files by `session_guid`

### Tasks:
- [x] Create data structure (dictionary) to group files by `session_guid`
- [x] Extract `session_guid` from validated file content
- [ ] Use filename as timestamp key for sorting within each session group
- [x] Store successfully validated files in memory grouped by session
- [x] Add logging for number of files per session
- [x] Test with sample files spanning multiple sessions
- [x] Verify all valid entries are grouped correctly
- [x] Write unit tests for grouping logic with mocked file data

## Step 4: Sort Session Entries and Collect Timestamps

### Tasks:
- [x] Sort each session's grouped files by timestamp (from filename)
- [x] Extract timestamp from filename format
- [x] Create ordered list of timestamps for each session
- [x] Prepare timestamp list for metadata inclusion
- [x] Verify output order matches timestamp order from filenames
- [x] Test that `timestamp_list` contains expected values
- [x] Write unit tests using mock filenames to confirm sort stability

## Step 5: Validate and Deduplicate `environment` per Session

### Tasks:
- [x] Check that all entries in a session have same `environment` value
- [x] Log warning when environment values differ within a session
- [x] Use first encountered `environment` value when conflicts exist
- [x] Store single `environment` value in session metadata
- [x] Create test data with consistent environments
- [x] Create test data with inconsistent environments
- [x] Verify warning is logged for inconsistent values
- [x] Confirm only one `environment` value is retained

## Step 6: Merge `session_data` Arrays

### Tasks:
- [x] For each session, concatenate all `session_data` arrays in timestamp order
- [x] Create single merged rrweb event stream per session
- [x] Preserve order of events within each file and across files
- [x] Store merged data as `rrweb_data` field
- [x] Test against sessions with known event counts
- [x] Verify merged `rrweb_data` matches total expected event count
- [x] Write unit tests with assertions for combined arrays

## Step 7: Save Final Session Objects to Compact JSON

### Tasks:
- [x] Create final session object structure with `session_guid`, `rrweb_data`, and `metadata`
- [x] Include `environment` and `timestamp_list` in metadata
- [x] Write each session to compact JSON file (no extra whitespace)
- [x] Name output files as `<session_guid>.json`
- [x] Save to specified target output directory
- [x] Create output directory if it doesn't exist
- [x] Verify output files are created with correct names
- [x] Check JSON format is compact
- [x] Test contents against expected structure

## Step 8: Add Summary Logging

### Tasks:
- [ ] Track total files processed during execution
- [ ] Count files skipped due to errors
- [ ] Count sessions successfully written
- [ ] Count warnings raised during processing
- [ ] Print/log summary at end of execution
- [ ] Include all counts in final summary
- [ ] Review log output after sample run
- [ ] Verify numbers match expectations
- [ ] Add small integration test with known file counts

## Step 9: Add CLI Interface (bucket name, output dir, verbosity)

### Tasks:
- [ ] Add command-line argument parsing using `argparse`
- [ ] Add `--bucket` argument for GCS bucket name
- [ ] Add `--output_dir` argument for output directory path
- [ ] Add `--verbose` or logging level arguments
- [ ] Set up logging configuration based on verbosity level
- [ ] Add `--help` message with usage instructions
- [ ] Test script with different CLI flags
- [ ] Verify behavior matches input arguments
- [ ] Test help message with `--help` flag
- [ ] Add validation for required arguments
