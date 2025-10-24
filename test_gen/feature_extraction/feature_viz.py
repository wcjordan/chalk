import json
import sys
from .models import UserInteraction, feature_chunk_from_dict

CHUNK_FILE = "data/output_features/0a93256e-c776-449f-9fea-4911466cf341_0a93256e-c776-449f-9fea-4911466cf341-chunk000.json"



def _extract_input_value(interaction: UserInteraction) -> dict:
    """Extract the input value helper."""
    return interaction.value.get('value')


def _is_same_input_interaction(last_input: UserInteraction, next_input: UserInteraction) -> bool:
    """
    Determine if the next input interaction is new compared to the last one.
    If they're part of the same typing sequence, return False so they can be combined.
    """
    if last_input is None or last_input.action != "input" or next_input.action != "input" or last_input.target_id != next_input.target_id:
        return False

    return _extract_input_value(last_input) in _extract_input_value(next_input)


def extract_dom_node_name(dom_nodes: dict, target_id: str) -> str:
    """Extract the DOM node name."""
    dom_node = dom_nodes.get(target_id)
    if dom_node.data_testid:
        return f"{dom_node.tag} w/ test_id=\"{dom_node.data_testid}\""
    return str(dom_node)


def print_input_interaction(dom_nodes: dict, interaction: dict):
    """Print the input interaction information."""
    dom_node_name = extract_dom_node_name(dom_nodes, interaction.target_id)
    print(f">   Typed into {dom_node_name}\n      \"{_extract_input_value(interaction)}\"")


def print_click_interaction(dom_nodes: dict, interation: dict):
    """Print the click interaction information."""
    dom_node_name = extract_dom_node_name(dom_nodes, interation.target_id)
    print(f">   Clicked on {dom_node_name}")


def print_dom_node(dom_nodes, target_id):
    """Print the DOM node information."""
    print(f"      {extract_dom_node_name(dom_nodes, target_id)}")


def print_interaction(dom_nodes, interaction):
    """Print a completed interaction."""
    if interaction is None:
        return

    if interaction.action == "input":
        print_input_interaction(dom_nodes, interaction)
    elif interaction.action == "click":
        print_click_interaction(dom_nodes, interaction)
    else:
        print(f">   {interaction}")
        print_dom_node(dom_nodes, interaction.target_id)


def main():
    """Main entry point for the CLI tool."""
    print(f"Using feature path: {CHUNK_FILE}")

    # Load and parse the chunk JSON
    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        chunk_data = json.load(f)

    # Validate chunk has required structure
    if not isinstance(chunk_data, dict) or "chunk_id" not in chunk_data:
        print(f"Warning: Skipping {CHUNK_FILE} - missing chunk_id")
        sys.exit(1)
    feature_chunk = feature_chunk_from_dict(chunk_data)
    dom_nodes = feature_chunk.features.get("ui_nodes", {})

    last_interaction = None
    for next_interaction in feature_chunk.features.get("interactions", []):

        # Skip prior interaction if the next one is part of the same typing sequence
        if _is_same_input_interaction(last_interaction, next_interaction):
            last_interaction = next_interaction
            continue

        print_interaction(dom_nodes, last_interaction)
        last_interaction = next_interaction

    if last_interaction is not None:
        print_interaction(dom_nodes, last_interaction)


if __name__ == "__main__":
    main()
