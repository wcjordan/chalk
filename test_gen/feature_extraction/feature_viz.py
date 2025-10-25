import json
from pathlib import Path
import sys
from .models import UserInteraction, feature_chunk_from_dict

INPUT_PATH = "data/output_features/"

class bcolors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    PINK = '\033[95m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_w_color(text: str, color_code: str):
    """Print text with color."""
    print(f"{color_code}{text}{bcolors.ENDC}")


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
    print_w_color(f">   Typed into {dom_node_name}\n      \"{_extract_input_value(interaction)}\"", bcolors.CYAN)


def print_interaction(dom_nodes, interaction):
    """Print a completed interaction."""
    if interaction is None:
        return

    dom_node_name = extract_dom_node_name(dom_nodes, interaction.target_id)
    if interaction.action == "input":
        print_input_interaction(dom_nodes, interaction)
    elif interaction.action == "click":
        print_w_color(f">   Clicked on {dom_node_name}", bcolors.GREEN)
    elif interaction.action == "scroll":
        print_w_color(f">   Scrolled {dom_node_name}", bcolors.YELLOW)
    else:
        print_w_color(f">   {interaction}", bcolors.RED)
        print_w_color(f"      {extract_dom_node_name(dom_nodes, interaction.target_id)}", bcolors.RED)
        raise ValueError(f"Unknown interaction action: {interaction.action}")


def main():
    """Main entry point for the CLI tool."""

    print(f"Using feature path: {INPUT_PATH}")
    chunk_files = list(Path(INPUT_PATH).glob("*.json"))
    for chunk_file in sorted(chunk_files):
        print(f"\n{bcolors.PINK}=== Interaction Sequence for {chunk_file.name} ==={bcolors.ENDC}")

        # Load and parse the chunk JSON
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)

        # Validate chunk has required structure
        if not isinstance(chunk_data, dict) or "chunk_id" not in chunk_data:
            print(f"Warning: Skipping {chunk_file} - missing chunk_id")
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
