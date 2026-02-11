# Plan: Clickable Links in Todos

## Goal
Make URLs in todo descriptions clickable, opening in a new browser tab.

## Constraints / Non-goals
- Only handle standard HTTP/HTTPS URLs
- Don't modify the backend data model (description remains TextField)
- Preserve existing todo display behavior for non-link text
- No markdown parsing (just URL detection)
- Keep the implementation simple and maintainable

## Stage 1: Add URL parsing utility
**Goal:** Create a utility to detect and parse URLs from text

**Steps:**
1. Create `ui/js/src/utils/urlParser.ts` with a function to detect URLs
2. Use a simple regex pattern for HTTP/HTTPS URLs
3. Return array of text segments with type (text vs link)
4. Add unit tests for the parser

**Exit criteria:**
- Parser correctly identifies URLs in text
- Parser handles edge cases (multiple URLs, URLs at start/end/middle)
- Tests pass

## Stage 2: Create LinkifiedText component
**Goal:** Component that renders text with clickable links

**Steps:**
1. Create `ui/js/src/components/LinkifiedText.tsx`
2. Use the URL parser utility
3. Render plain text segments as Text
4. Render URL segments as pressable/clickable Text
5. Handle platform differences (web vs native)
6. Style links appropriately (underline, color)

**Exit criteria:**
- Component renders mixed text and links correctly
- Links are visually distinct (underlined, colored)
- Pressing links opens URLs correctly on both web and native

## Stage 3: Integrate into TodoItem
**Goal:** Replace plain Text in TodoItem with LinkifiedText

**Steps:**
1. Import LinkifiedText in TodoItem.tsx
2. Replace the description Text component with LinkifiedText
3. Pass through existing styles
4. Update tests/snapshots if needed

**Exit criteria:**
- TodoItem displays clickable links
- Existing tests pass
- UI snapshots updated if needed

## Stage 4: Add E2E test
**Goal:** Verify link clicking works end-to-end

**Steps:**
1. Add a Playwright test that creates a todo with a URL
2. Verify the link is rendered
3. Verify clicking opens the URL (mock or stub the open)

**Exit criteria:**
- E2E test passes
- Test covers both creating and clicking links

## Stage 5: Final verification and cleanup
**Goal:** Ensure all quality gates pass

**Steps:**
1. Run all tests and linting
2. Manual testing on web and native (Expo Go)
3. Update documentation if needed
4. Commit changes

**Exit criteria:**
- All tests pass
- All linting passes
- Manual verification complete
- Changes committed
