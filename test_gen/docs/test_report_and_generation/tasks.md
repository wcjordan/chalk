### 📋 **Task List with Rough Estimates**

---

| Phase                         | Tasks                                                                                                                                                                                       | Est. Time |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| **Phase 1: CLI Foundation**   | - Set up Python CLI scaffolding (`click` or similar)<br>- Define subcommands: `analyze`, `report`, `generate`<br>- Create config + input argument handling                                  | 2–3 days  |
| **Phase 2: Session Analysis** | - Write session file loader<br>- Build LLM integration layer (pluggable)<br>- Develop rule-based matcher + bootstrap logic<br>- Generate initial mappings + confidence scores               | 4–6 days  |
| **Phase 3: Reporting**        | - Create combined report generator (YAML or markdown)<br>- Highlight unknowns / low-confidence<br>- Parse + ingest manual corrections from report                                           | 3–4 days  |
| **Phase 4: Test Generation**  | - Write Playwright Python test generator<br>- Build helper module generator with descriptions<br>- Embed metadata + workflow mappings<br>- Write output files directly into `tests/` folder | 5–7 days  |
| **Phase 5: Learning System**  | - Implement feedback history tracking in flat files<br>- Update analyzer to load + use past feedback<br>- Refine rules + improve prompt context                                             | 4–6 days  |
| **Integration + Review**      | - Hook into existing repo + branch/PR flow<br>- Manual testing + iteration<br>- Initial developer docs / README                                                                             | 3–4 days  |

