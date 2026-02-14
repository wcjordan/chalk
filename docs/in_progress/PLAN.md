# Plan: Etag System Implementation

## Goal
Prevent stale server updates from overwriting recent user changes by implementing a version field.

## Stages

### Stage 1: Server-Side Version Field ⏳
- Add version field to TodoModel
- Update serializer to include version
- Create and run migration
- Verify with tests
- **Commit:** "Add version field to TodoModel for etag support"

### Stage 2: Client Type Updates
- Add version to TypeScript Todo and TodoPatch interfaces
- Verify TypeScript compilation
- **Commit:** "Add version field to client Todo types"

### Stage 3: Version-Aware Update Logic
- Modify updateTodoInPlace() to check versions
- Skip stale updates (server version < local version)
- Add console logging for debugging
- **Commit:** "Add version checking to prevent stale server updates"

### Stage 4: Server Tests
- Test version initialization (version=1)
- Test version increment on update
- Test serializer includes version
- **Commit:** "Add server tests for version field"

### Stage 5: Client Tests
- Test updateTodoInPlace version checking
- Test stale update rejection
- Test fresh update acceptance
- **Commit:** "Add client tests for etag version checking"
