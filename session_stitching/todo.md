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
- [ ] Write unit tests using mocks for GCS interaction

## Step 2: Parse and Validate a Single JSON File

### Tasks:
- [ ] Create function to parse JSON content from file data
- [ ] Add validation for required fields: `session_guid`, `session_data`, `environment`
- [ ] Handle malformed JSON gracefully with try/catch
- [ ] Handle missing required fields with appropriate error messages
- [ ] Add logging for validation failures
- [ ] Create test files: valid JSON, missing fields, corrupt format
- [ ] Test parsing function on each test file type
- [ ] Verify error handling works as expected
- [ ] Write unit tests for edge cases (empty files, wrong data types, etc.)

## Step 3: Group Valid Files by `session_guid`

### Tasks:
- [ ] Create data structure (dictionary) to group files by `session_guid`
- [ ] Extract `session_guid` from validated file content
- [ ] Use filename as timestamp key for sorting within each session group
- [ ] Store successfully validated files in memory grouped by session
- [ ] Add logging for number of files per session
- [ ] Test with sample files spanning multiple sessions
- [ ] Verify all valid entries are grouped correctly
- [ ] Write unit tests for grouping logic with mocked file data

## Step 4: Sort Session Entries and Collect Timestamps

### Tasks:
- [ ] Sort each session's grouped files by timestamp (from filename)
- [ ] Extract timestamp from filename format
- [ ] Create ordered list of timestamps for each session
- [ ] Prepare timestamp list for metadata inclusion
- [ ] Verify output order matches timestamp order from filenames
- [ ] Test that `timestamp_list` contains expected values
- [ ] Write unit tests using mock filenames to confirm sort stability

## Step 5: Validate and Deduplicate `environment` per Session

### Tasks:
- [ ] Check that all entries in a session have same `environment` value
- [ ] Log warning when environment values differ within a session
- [ ] Use first encountered `environment` value when conflicts exist
- [ ] Store single `environment` value in session metadata
- [ ] Create test data with consistent environments
- [ ] Create test data with inconsistent environments
- [ ] Verify warning is logged for inconsistent values
- [ ] Confirm only one `environment` value is retained

## Step 6: Merge `session_data` Arrays

### Tasks:
- [ ] For each session, concatenate all `session_data` arrays in timestamp order
- [ ] Create single merged rrweb event stream per session
- [ ] Preserve order of events within each file and across files
- [ ] Store merged data as `rrweb_data` field
- [ ] Test against sessions with known event counts
- [ ] Verify merged `rrweb_data` matches total expected event count
- [ ] Write unit tests with assertions for combined arrays

## Step 7: Save Final Session Objects to Compact JSON

### Tasks:
- [ ] Create final session object structure with `session_guid`, `rrweb_data`, and `metadata`
- [ ] Include `environment` and `timestamp_list` in metadata
- [ ] Write each session to compact JSON file (no extra whitespace)
- [ ] Name output files as `<session_guid>.json`
- [ ] Save to specified target output directory
- [ ] Create output directory if it doesn't exist
- [ ] Verify output files are created with correct names
- [ ] Check JSON format is compact
- [ ] Test contents against expected structure

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
