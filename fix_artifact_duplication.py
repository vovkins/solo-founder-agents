#!/usr/bin/env python3
"""Fix logic duplication in artifact type mapping."""

# Read artifact_manager.py
with open("src/tools/artifact_manager.py", "r") as f:
    content = f.read()

# Add helper function after ArtifactType enum
helper_code = '''

def get_artifact_type_from_string(type_str: str) -> Optional[ArtifactType]:
    """Convert string to ArtifactType enum.

    Args:
        type_str: String representation of artifact type

    Returns:
        ArtifactType enum or None if not found
    """
    type_map = {
        "prd": ArtifactType.PRD,
        "system-design": ArtifactType.SYSTEM_DESIGN,
        "adr": ArtifactType.ADR,
        "design-system": ArtifactType.DESIGN_SYSTEM,
        "ui-screen": ArtifactType.UI_SCREEN,
        "user-flow": ArtifactType.USER_FLOW,
        "test-case": ArtifactType.TEST_CASE,
        "test-run-log": ArtifactType.TEST_RUN_LOG,
    }
    return type_map.get(type_str)

'''

# Insert after ArtifactType enum
insert_pos = content.find('\nclass ArtifactManager:')
if insert_pos != -1:
    content = content[:insert_pos] + helper_code + content[insert_pos:]

# Write back
with open("src/tools/artifact_manager.py", "w") as f:
    f.write(content)

print("✅ Added helper function to artifact_manager.py")

# Now update artifact_tools.py to use the helper
with open("src/tools/artifact_tools.py", "r") as f:
    content = f.read()

# Replace type_map logic with helper function call
old_code = '''        type_map = {
            "prd": ArtifactType.PRD,
            "system-design": ArtifactType.SYSTEM_DESIGN,
            "adr": ArtifactType.ADR,
            "design-system": ArtifactType.DESIGN_SYSTEM,
            "ui-screen": ArtifactType.UI_SCREEN,
            "user-flow": ArtifactType.USER_FLOW,
            "test-case": ArtifactType.TEST_CASE,
            "test-run-log": ArtifactType.TEST_RUN_LOG,
        }
        if artifact_type not in type_map:
            return f"Error: Unknown artifact type '{artifact_type}'. Valid types: {list(type_map.keys())}"

        artifact_type_enum = type_map[artifact_type]'''

new_code = '''        from .artifact_manager import get_artifact_type_from_string

        artifact_type_enum = get_artifact_type_from_string(artifact_type)
        if artifact_type_enum is None:
            return f"Error: Unknown artifact type '{artifact_type}'."'''

content = content.replace(old_code, new_code)

# Write back
with open("src/tools/artifact_tools.py", "w") as f:
    f.write(content)

print("✅ Updated artifact_tools.py to use helper function")
