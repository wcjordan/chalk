import json
from pathlib import Path
import sys
from .models import UserInteraction, feature_chunk_from_dict

INPUT_PATH = "data/output_features/"


class bcolors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    PINK = "\033[95m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_w_color(text: str, color_code: str):
    """Print text with color."""
    print(f"{color_code}{text}{bcolors.ENDC}")


def create_dom_path_to_node_dict(dom_nodes: dict) -> dict:
    """Create a mapping from DOM paths to nodes."""
    dom_path_to_node = {}
    for node in dom_nodes.values():
        dom_path_to_node[node.dom_path] = node
    return dom_path_to_node


def _extract_input_value(interaction: UserInteraction) -> dict:
    """Extract the input value helper."""
    return interaction.value.get("value")


def _is_same_input_interaction(
    last_input: UserInteraction, next_input: UserInteraction
) -> bool:
    """
    Determine if the next input interaction is new compared to the last one.
    If they're part of the same typing sequence, return False so they can be combined.
    """
    if (
        last_input is None
        or last_input.action != "input"
        or next_input.action != "input"
        or last_input.target_id != next_input.target_id
    ):
        return False

    return _extract_input_value(last_input) in _extract_input_value(next_input)


def extract_dom_node_name(
    dom_nodes: dict, dom_path_to_node: dict, target_id: str
) -> str:
    """Extract the DOM node name."""
    dom_node = dom_nodes.get(target_id)
    if dom_node.data_testid:
        return f'{dom_node.tag} w/ test_id="{dom_node.data_testid}"'

    if dom_node.dom_path is None:
        return str(dom_node)

    # Find a parent with a data-testid if possible
    rest = []
    dom_path = dom_node.dom_path
    while " > " in dom_path:
        path_split = dom_path.rsplit(" > ", 1)
        parent_path = path_split[0].strip()
        rest.insert(0, path_split[-1].strip())
        parent_node = dom_path_to_node.get(parent_path)

        if parent_node and parent_node.data_testid:
            rest_str = " > ".join(rest)
            return f'{dom_node.tag} w/ test_id="{parent_node.data_testid}" > {rest_str}'

        dom_path = parent_path
    print_w_color(f"Unknown dom node: {dom_node}", bcolors.RED)
    return str(dom_node)


def print_input_interaction(dom_node_name: str, interaction: dict):
    """Print the input interaction information."""
    print_w_color(
        f'>   Typed into {dom_node_name}\n      "{_extract_input_value(interaction)}"',
        bcolors.CYAN,
    )


def print_interaction(
    dom_nodes: dict, dom_path_to_node: dict, interaction: UserInteraction
):
    """Print a completed interaction."""
    if interaction is None:
        return

    dom_node_name = extract_dom_node_name(
        dom_nodes, dom_path_to_node, interaction.target_id
    )
    if interaction.action == "input":
        print_input_interaction(dom_node_name, interaction)
    elif interaction.action == "click":
        print_w_color(f">   Clicked on {dom_node_name}", bcolors.GREEN)
    elif interaction.action == "scroll":
        print_w_color(f">   Scrolled {dom_node_name}", bcolors.YELLOW)
    else:
        print_w_color(f">   {interaction}", bcolors.RED)
        print_w_color(
            f"      {extract_dom_node_name(dom_nodes, interaction.target_id)}",
            bcolors.RED,
        )
        raise ValueError(f"Unknown interaction action: {interaction.action}")


def main():
    """Main entry point for the CLI tool."""

    print(f"Using feature path: {INPUT_PATH}")
    chunk_files = list(Path(INPUT_PATH).glob("*.json"))
    total_files = len(chunk_files)
    for chunk_file in sorted(chunk_files):
        print_w_color(
            f"\n=== Interaction Sequence for {chunk_file.name} ===", bcolors.PINK
        )

        # Load and parse the chunk JSON
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)

        # Validate chunk has required structure
        if not isinstance(chunk_data, dict) or "chunk_id" not in chunk_data:
            print(f"Warning: Skipping {chunk_file} - missing chunk_id")
            sys.exit(1)
        feature_chunk = feature_chunk_from_dict(chunk_data)
        dom_nodes = feature_chunk.features.get("ui_nodes", {})
        dom_path_to_node = create_dom_path_to_node_dict(dom_nodes)

        last_interaction = None
        for next_interaction in feature_chunk.features.get("interactions", []):

            # Skip prior interaction if the next one is part of the same typing sequence
            if _is_same_input_interaction(last_interaction, next_interaction):
                last_interaction = next_interaction
                continue

            print_interaction(dom_nodes, dom_path_to_node, last_interaction)
            last_interaction = next_interaction

        if last_interaction is not None:
            print_interaction(dom_nodes, dom_path_to_node, last_interaction)
    print(f"Printed {total_files} feature chunk files.")


if __name__ == "__main__":
    main()
