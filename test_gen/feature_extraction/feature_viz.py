import json
from pprint import pprint
import sys
from .models import UserInteraction, feature_chunk_from_dict

CHUNK_FILE = "data/output_features/0a93256e-c776-449f-9fea-4911466cf341_0a93256e-c776-449f-9fea-4911466cf341-chunk000.json"



def extract_input_interaction(interaction: UserInteraction) -> dict:
    """Extract the input feature chunk for debugging."""
    return {
        'target_id': interaction.target_id,
        'input_value': interaction.value.get('value'),
    }


def is_new_input_interaction(last_input: dict, next_input: dict) -> bool:
    """
    Determine if the next input interaction is new compared to the last one.
    If they're part of the same typing sequence, return False so they can be combined.
    """
    if last_input is None:
        return True

    # print(last_input.get('input_value') in next_input.get('input_value'))
    if last_input.get('target_id') == next_input.get('target_id') and last_input.get('input_value') in next_input.get('input_value'):
        return False
    return True


def extract_dom_node_name(dom_nodes: dict, target_id: str) -> str:
    """Extract the DOM node name."""
    dom_node = dom_nodes.get(target_id)
    if dom_node.data_testid:
        return f"{dom_node.tag} w/ test_id=\"{dom_node.data_testid}\""
    return str(dom_node)


def print_input_interaction(dom_nodes: dict, interaction: dict):
    """Print the input interaction information for debugging."""
    if interaction is None:
        return
    dom_node_name = extract_dom_node_name(dom_nodes, interaction['target_id'])
    print(f"Typed \"{interaction['input_value']}\" into {dom_node_name}")
    print()


def print_dom_node(dom_nodes, target_id):
    """Print the DOM node information for debugging."""
    print(extract_dom_node_name(dom_nodes, target_id))
    print()


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

    last_input_interaction = None
    for interaction in feature_chunk.features.get("interactions", []):
        if interaction.action != "input":
            if last_input_interaction is not None:
                print_input_interaction(dom_nodes, last_input_interaction)
                last_input_interaction = None

            print(interaction)
            print_dom_node(dom_nodes, interaction.target_id)

        else:
            next_input_interaction = extract_input_interaction(interaction)
            if is_new_input_interaction(last_input_interaction, next_input_interaction):
                print_input_interaction(dom_nodes, last_input_interaction)
                last_input_interaction = next_input_interaction
            else:
                # Combine input interactions
                last_input_interaction = next_input_interaction

    if last_input_interaction is not None:
        print_input_interaction(dom_nodes, last_input_interaction)
        last_input_interaction = None


if __name__ == "__main__":
    main()
