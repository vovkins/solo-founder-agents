"""Main entry point for Solo Founder Agents."""

from src.crews import run_core_crew
from config.settings import settings


def main():
    """Main function to run the application."""
    print("🚀 Solo Founder Agents")
    print(f"📦 Repository: {settings.github_repo}")
    print(f"🤖 Developer LLM: {settings.llm_developer}")
    print(f"👀 Reviewer LLM: {settings.llm_reviewer}")
    print("\nSystem initialized. Ready to process tasks.")


def process_vision(founder_vision: str):
    """Process founder's product vision through the core crew.

    Args:
        founder_vision: The founder's product idea/requirements

    Returns:
        Dictionary with results
    """
    print(f"\n📋 Processing founder vision...")
    print(f"Input: {founder_vision[:100]}...")

    result = run_core_crew(founder_vision)

    print("\n✅ Processing complete!")
    print(f"Artifacts created:")
    for name, path in result.get("artifacts", {}).items():
        print(f"  - {name}: {path}")

    return result


if __name__ == "__main__":
    main()
