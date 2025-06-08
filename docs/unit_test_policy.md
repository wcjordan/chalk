## 🧪 Unit Test Policy & Guidance for Coding Agents

**Purpose:**
Support the creation of reliable, maintainable unit tests that verify behavior without coupling to implementation details. Reduce test fragility over time as code evolves.

---

### 🔧 Principles for Writing Unit Tests

1. **Test Public Interfaces Only**

   * Write tests that call exported/public functions, classes, or modules.
   * Avoid testing private helpers unless:

     * They are reused across multiple entry points
     * They encapsulate complex, domain-relevant logic

2. **Write Behavior-Focused Tests**

   * Test what the software *should do*, not how it works internally.
   * Use clear, domain-driven names like:

     * `test_removes_invalid_items`
     * `test_preserves_sorted_order`

3. **Assert Meaningful Outcomes**

   * Validate return values, state changes, or side effects.
   * Prefer property or constraint checks (e.g., "output contains no duplicates") over fragile value comparisons.

4. **Use Minimal Realistic Inputs**

   * Keep test inputs as small and readable as possible.
   * Focus on edge cases and representative inputs for each test.

5. **Avoid Redundant Stage-Level Testing**

   * If the final-stage test exercises earlier steps, rely on it unless earlier logic is reused or fragile.
   * Don’t manually simulate internal pipeline stages unless testing them independently is justified.

---

### 🔍 Test Maintenance and Pruning Guidance

1. **Use Code Coverage to Guide Decisions**

   * After merging high-level tests, run coverage tools to identify untested paths.
   * Prune low-level tests that are now covered by higher-level tests.

2. **Remove Tests of Internal Artifacts**

   * Delete tests that only validate intermediate data unless:

     * The data is externally meaningful
     * It helps isolate important failure modes

3. **Consolidate to Black-Box Pipeline Tests**

   * Where appropriate, test full data transformations via high-level interfaces.
   * Validate input-output behavior using constraints or full examples.

4. **Convert Fragile Unit Tests to Integration Tests**

   * If a test validates a sequence of steps across functions, consider moving it to an integration or functional test suite.

---

### 🧹 Test Hygiene Conventions

* **Mark scaffold tests** with `# TEMP: remove after integration` or prefix as `_test_temp_case`.
* Mirror source file structure in test directories (e.g., `src/foo.py` → `tests/test_foo.py`).
* Regularly revisit test suites to prune, consolidate, and validate with coverage tools.

---

## 📘 Appendix: Python + Pytest Specifics

### 📂 File & Directory Conventions

* Use `tests/` directory with mirrored module structure
* Test files: `test_<module>.py`
* Test functions: `def test_<behavior>():`

### 🧪 Pytest Practices

* Use fixtures for reusable setup (`@pytest.fixture`)
* Avoid mocking internal logic unless necessary
* Use parametrized tests for variations:

  ```python
  @pytest.mark.parametrize("input,expected", [...])
  def test_behavior(input, expected):
      assert transform(input) == expected
  ```

### 📈 Coverage Tools

* Use `pytest-cov` to measure coverage:

  ```bash
  pytest --cov=src tests/
  ```
* Focus coverage thresholds on public APIs, not private/internal helpers

### ⚠️ Common Pitfalls to Avoid

* Don’t assert internal state unless it’s exposed via the API
* Don’t use brittle snapshots or golden files for logic-heavy transforms—prefer invariants and constraints
