                  ┌────────────────────────────-──┐
                  │      Local rrweb Session      │
                  │   JSON Files (per session)    │
                  └──────────────┬──────────────-─┘
                                 │
                                 ▼
                  ┌────────────────────────────-----──┐
                  │       CLI Command: analyze.       │
                  │  - LLM API Interface (pluggable)  │
                  │  - Rule-based Pattern Matching    │
                  └──────────────┬───────────────-----┘
                                 │
                      Generates Initial Mappings
                                 │
                                 ▼
                  ┌───────────────────────────--───┐
                  │  Mapping & Feedback Flat Files │
                  │   - workflow_mappings.yaml     │
                  │   - known_rules.yaml           │
                  │   - feedback_history.yaml      │
                  └──────────────┬──────────────--─┘
                                 │
                  ┌──────────────┴─────────────---------──┐
                  │      CLI Command: report              │
                  │  - Generate combined report           │
                  │  - Highlight unknowns, low confidence │
                  └──────────────┬─────────────---------──┘
                                 │
                           Human Review & Edit
                                 │
                                 ▼
                  ┌─────────────────────────────----─┐
                  │      CLI Command: generate       │
                  │  - Test Code Generator           │
                  │  - Helper Function Generator     │
                  │  - Embed Descriptions + Metadata │
                  └──────────────┬──────────────----─┘
                                 │
                  ┌──────────────┴───────────────-┐
                  │  Direct Output to `tests/`    │
                  │  - Playwright Python Tests    │
                  │  - Helpers Module             │
                  └──────────────┬───────────────-┘
                                 │
                      Used in CI + Local Test Runs

