"""Tasks for UI/UX Designer agent."""

from crewai import Task

from src.agents import designer_agent


def create_design_system_task(system_design_path: str) -> Task:
    """Create task for generating design system.

    Args:
        system_design_path: Path to System Design document

    Returns:
        Task for design system creation
    """
    return Task(
        description=f"""
        Create a comprehensive design system.
        
        System Design: {system_design_path}
        
        Follow the template from templates/design-system.md and include:
        
        1. **Color Palette**
           - Primary colors (main, light, dark)
           - Secondary colors
           - Semantic colors (success, warning, error, info)
           - Neutral colors (background, text, borders)
           - Color contrast ratios for accessibility
        
        2. **Typography**
           - Font families (headings, body, mono)
           - Font sizes scale (xs, sm, base, lg, xl, 2xl, etc.)
           - Font weights
           - Line heights
           - Letter spacing
        
        3. **Spacing**
           - Spacing scale (0, 1, 2, 3, 4, 6, 8, 12, 16, 24, etc.)
           - Padding conventions
           - Margin conventions
           - Gap values
        
        4. **Components**
           - Button variants (primary, secondary, outline, ghost)
           - Input fields
           - Cards
           - Navigation
           - Modals
           - Lists
           - Forms
        
        5. **Borders & Radius**
           - Border widths
           - Border radius scale
           - Shadow scale
        
        6. **Breakpoints**
           - Mobile (< 640px)
           - Tablet (640px - 1024px)
           - Desktop (> 1024px)
        
        7. **Accessibility**
           - WCAG 2.1 AA requirements
           - Focus indicators
           - Color contrast
           - Screen reader considerations
        
        Save to docs/design-system.md
        """,
        expected_output="Path to the created design system document",
        agent=designer_agent,
    )


def create_ui_screen_task(screen_name: str, requirements: str) -> Task:
    """Create task for generating UI specification for a screen.

    Args:
        screen_name: Name of the screen (e.g., 'LoginScreen')
        requirements: Requirements for the screen

    Returns:
        Task for UI spec creation
    """
    return Task(
        description=f"""
        Create UI specification for {screen_name}.
        
        Requirements:
        {requirements}
        
        Follow the template from templates/ui-screen.md and include:
        
        1. **Overview**
           - Screen purpose
           - User goals
        
        2. **Layout**
           - Visual structure (Mermaid diagram)
           - Responsive behavior
           - Grid system
        
        3. **Components**
           - List of components used
           - Component properties
           - States
        
        4. **Content**
           - Text content
           - Images/icons
           - Empty states
        
        5. **Interactions**
           - User actions
           - Transitions
           - Animations
        
        6. **Accessibility**
           - ARIA labels
           - Keyboard navigation
           - Screen reader text
        
        Save to docs/ui/screens/{screen_name}.md
        """,
        expected_output=f"Path to the created UI spec for {screen_name}",
        agent=designer_agent,
    )


def create_user_flow_task(flow_name: str, steps: str) -> Task:
    """Create task for generating user flow diagram.

    Args:
        flow_name: Name of the user flow (e.g., 'User Registration')
        steps: Steps in the flow

    Returns:
        Task for user flow creation
    """
    return Task(
        description=f"""
        Create user flow diagram for {flow_name}.
        
        Steps:
        {steps}
        
        Follow the template from templates/user-flow.md and include:
        
        1. **Overview**
           - Flow purpose
           - User type
        
        2. **Flow Diagram**
           - Mermaid flowchart
           - Decision points
           - Error paths
        
        3. **Steps**
           - Detailed step descriptions
           - Screen for each step
           - User actions
        
        4. **Edge Cases**
           - Alternative paths
           - Error handling
           - Back navigation
        
        Save to docs/user-flows/{flow_name}.md
        """,
        expected_output=f"Path to the created user flow for {flow_name}",
        agent=designer_agent,
    )


def create_component_spec_task(
    component_name: str,
    description: str,
) -> Task:
    """Create task for component specification.

    Args:
        component_name: Name of the component
        description: Component description and requirements

    Returns:
        Task for component spec creation
    """
    return Task(
        description=f"""
        Create component specification for {component_name}.
        
        Description:
        {description}
        
        Include:
        
        1. **Props Interface**
           - TypeScript interface
           - Required vs optional props
           - Default values
        
        2. **Variants**
           - Visual variants
           - Size variants
        
        3. **States**
           - Default
           - Hover
           - Focus
           - Active
           - Disabled
           - Loading
        
        4. **Usage Examples**
           - Code examples
           - Common patterns
        
        5. **Accessibility**
           - ARIA attributes
           - Keyboard interactions
        
        Add to docs/components/{component_name}.md
        """,
        expected_output=f"Path to the created component spec for {component_name}",
        agent=designer_agent,
    )


def create_all_screens_task(
    design_system_path: str,
    screens_list: list,
) -> Task:
    """Create task for generating all UI screens.

    Args:
        design_system_path: Path to design system
        screens_list: List of screens to create

    Returns:
        Task for all screens creation
    """
    screens_str = "\n".join(f"- {screen}" for screen in screens_list)

    return Task(
        description=f"""
        Create UI specifications for all screens.
        
        Design System: {design_system_path}
        
        Screens to create:
        {screens_str}
        
        For each screen:
        1. Analyze requirements
        2. Design layout structure
        3. Specify components
        4. Define interactions
        5. Ensure accessibility
        
        Save each to docs/ui/screens/[ScreenName].md
        """,
        expected_output="List of created screen specification paths",
        agent=designer_agent,
    )
