"""
Utility python script which can extract a specific prompt from the prompt_plan.md markdown file.
This is handy for passing a specific prompt to the LLM for executing on implementation steps.
"""

PROMPT_NUMBER = "1"
PROMPT_DIR = "test_gen/docs/rules_based_action_matching"

print(f"- Directory of with `spec.md` and `prompt_plan.md`: \"{PROMPT_DIR}\"")
print(f"- Step number: {PROMPT_NUMBER}")
print("- Prompt Details:")

FOUND = False
with open(f"{PROMPT_DIR}/prompt_plan.md", 'r', encoding='utf-8') as file:
    for line in file:
        if line.startswith(f"### **Step {PROMPT_NUMBER}:"):
            FOUND = True
        elif FOUND and line.startswith("### **"):
            break

        if FOUND:
            print(f"    {line.strip()}")
