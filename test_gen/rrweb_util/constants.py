"""
Shared constants for rrweb event processing across all modules.
"""

# pylint: disable=too-few-public-methods


class EventType:
    """rrweb event type constants."""

    # sync w/
    # https://github.com/rrweb-io/rrweb/blob/4db9782d1278a2b7235ed48162ccedf0e0952113/packages/types/src/index.ts
    DOM_CONTENT_LOADED = 0
    LOAD = 1
    FULL_SNAPSHOT = 2
    INCREMENTAL_SNAPSHOT = 3
    META = 4
    CUSTOM = 5
    PLUGIN = 6


class IncrementalSource:
    """rrweb incremental snapshot source constants."""

    # sync w/
    # https://github.com/rrweb-io/rrweb/blob/4db9782d1278a2b7235ed48162ccedf0e0952113/packages/types/src/index.ts#L62
    MUTATION = 0
    MOUSE_MOVE = 1
    MOUSE_INTERACTION = 2
    SCROLL = 3
    VIEWPORT_RESIZE = 4
    INPUT = 5
    TOUCH_MOVE = 6
    MEDIA_INTERACTION = 7
    STYLE_SHEET_RULE = 8
    CANVAS_MUTATION = 9
    FONT = 10
    LOG = 11
    DRAG = 12
    STYLE_DECLARATION = 13
    SELECTION = 14
    ADOPTED_STYLE_SHEET = 15
    CUSTOM_ELEMENT = 16


class MouseInteractionType:
    """Mouse interaction type constants."""

    # sync w/
    # https://github.com/rrweb-io/rrweb/blob/4db9782d1278a2b7235ed48162ccedf0e0952113/packages/types/src/index.ts#L359
    MOUSE_UP = 0
    MOUSE_DOWN = 1
    CLICK = 2
    CONTEXT_MENU = 3
    DBL_CLICK = 4
    FOCUS = 5
    BLUR = 6
    TOUCH_START = 7
    TOUCH_MOVE_DEPARTED = 8
    TOUCH_END = 9
    TOUCH_CANCEL = 10


class NodeType:
    """DOM node type constants (sync with rrweb's NodeType enum)."""

    # sync w/
    # https://github.com/rrweb-io/rrweb/blob/4db9782d1278a2b7235ed48162ccedf0e0952113/packages/rrdom/src/document.ts#L753
    PLACEHOLDER = 0
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_REFERENCE_NODE = 5
    ENTITY_NODE = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    DOCUMENT_FRAGMENT_NODE = 11


# Node type to tag name mapping
NODE_TYPE_TO_TAG_MAP = {
    NodeType.PLACEHOLDER: "placeholder",
    NodeType.ELEMENT_NODE: "element_node",
    NodeType.ATTRIBUTE_NODE: "attribute_node",
    NodeType.TEXT_NODE: "text_node",
    NodeType.CDATA_SECTION_NODE: "cdata_section_node",
    NodeType.ENTITY_REFERENCE_NODE: "entity_reference_node",
    NodeType.ENTITY_NODE: "entity_node",
    NodeType.PROCESSING_INSTRUCTION_NODE: "processing_instruction_node",
    NodeType.COMMENT_NODE: "comment_node",
    NodeType.DOCUMENT_NODE: "document_node",
    NodeType.DOCUMENT_TYPE_NODE: "document_type_node",
    NodeType.DOCUMENT_FRAGMENT_NODE: "document_fragment_node",
}
