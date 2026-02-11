# Verification Steps

## Per Stage

### Stage 1: URL Parser
```bash
cd /Users/flipperkid/git/chalk/ui
make test
```
**Expected:** Tests for urlParser.ts pass

### Stage 2: LinkifiedText Component
```bash
cd /Users/flipperkid/git/chalk/ui
make test
```
**Expected:** Tests for LinkifiedText.tsx pass

### Stage 3: TodoItem Integration
```bash
cd /Users/flipperkid/git/chalk/ui
make test
```
**Expected:** All UI tests pass (may need snapshot update)

If snapshots need updating:
```bash
cd /Users/flipperkid/git/chalk/ui
make update-snapshots
```

### Stage 4: E2E Test
```bash
cd /Users/flipperkid/git/chalk/tests
make test
```
**Expected:** New link clicking test passes

## Final Verification

### All Tests and Linting
```bash
cd /Users/flipperkid/git/chalk
make test
```
**Expected:** All tests and linting pass

### Format Check
```bash
cd /Users/flipperkid/git/chalk/ui
make format
```
**Expected:** Code is properly formatted

### Manual Testing
1. Start the app: `cd ui && npm start`
2. Create a todo with text like: "Check out https://example.com for info"
3. Verify the URL is underlined and colored
4. Click the URL
5. Verify it opens in a new tab (web) or browser (native)

**Expected:** Links are clickable and open correctly

## Success Criteria
- ✅ All unit tests pass
- ✅ All E2E tests pass
- ✅ Linting passes
- ✅ Snapshots updated if needed
- ✅ Manual verification complete
- ✅ No new console errors or warnings
