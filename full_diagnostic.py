#!/usr/bin/env python3
"""Полный диагностический анализ solo-founder-agents."""

import sys
import traceback
from pathlib import Path

print("=" * 80)
print("🔍 FULL SYSTEM DIAGNOSTIC")
print("=" * 80)

# TEST 1: Check prompts exist
print("\n1️⃣ PROMPT FILES:")
print("-" * 80)

prompt_dir = Path("prompts")
if not prompt_dir.exists():
    print("❌ CRITICAL: prompts/ directory doesn't exist!")
    sys.exit(1)

required_prompts = [
    "pm/system-prompt.md",
    "analyst/system-prompt.md",
    "architect/system-prompt.md",
    "designer/system-prompt.md",
    "developer/system-prompt.md",
    "reviewer/system-prompt.md",
    "qa/system-prompt.md",
    "tech_writer/system-prompt.md",
]

missing = []
for prompt in required_prompts:
    path = prompt_dir / prompt
    if path.exists():
        size = path.stat().st_size
        print(f"✅ {prompt} ({size} bytes)")
    else:
        print(f"❌ {prompt} MISSING!")
        missing.append(prompt)

if missing:
    print(f"\n❌ CRITICAL: {len(missing)} prompt files missing!")
    sys.exit(1)

# TEST 2: Check AgentFactory initialization
print("\n2️⃣ AGENT FACTORY INITIALIZATION:")
print("-" * 80)

try:
    from src.agents.factory import agent_factory
    print(f"✅ AgentFactory initialized")
    agents_count = len(agent_factory._config.get('agents', []))
    print(f"   Config loaded: {agents_count} agents")
except Exception as e:
    print(f"❌ CRITICAL: AgentFactory failed!")
    print(f"   Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# TEST 3: Check agent creation
print("\n3️⃣ AGENT CREATION:")
print("-" * 80)

try:
    from src.agents import get_pm_agent, get_analyst_agent
    
    print("Creating PM agent...")
    pm_agent = get_pm_agent()
    print(f"✅ PM Agent created: {pm_agent.role}")
    print(f"   Goal: {pm_agent.goal[:80]}...")
    print(f"   Tools: {len(pm_agent.tools)} tools")
    
    print("\nCreating Analyst agent...")
    analyst_agent = get_analyst_agent()
    print(f"✅ Analyst Agent created: {analyst_agent.role}")
    print(f"   Goal: {analyst_agent.goal[:80]}...")
    print(f"   Tools: {len(analyst_agent.tools)} tools")
    
except Exception as e:
    print(f"❌ CRITICAL: Agent creation failed!")
    print(f"   Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# TEST 4: Check crew creation
print("\n4️⃣ CREW CREATION:")
print("-" * 80)

try:
    from src.crews.pm_crew import create_pm_crew
    from src.crews.analyst_crew import create_analyst_crew
    
    print("Creating PM crew...")
    pm_crew = create_pm_crew("Test founder vision")
    print(f"✅ PM Crew created")
    print(f"   Agents: {len(pm_crew.agents)}")
    print(f"   Tasks: {len(pm_crew.tasks)}")
    
    # Check task-agent binding
    for i, task in enumerate(pm_crew.tasks, 1):
        agent_role = task.agent.role if task.agent else "None"
        print(f"   Task {i}: {task.description[:60]}...")
        print(f"      Agent: {agent_role}")
    
    print("\nCreating Analyst crew...")
    analyst_crew = create_analyst_crew()
    print(f"✅ Analyst Crew created")
    print(f"   Agents: {len(analyst_crew.agents)}")
    print(f"   Tasks: {len(analyst_crew.tasks)}")
    
    # Check task-agent binding
    for i, task in enumerate(analyst_crew.tasks, 1):
        agent_role = task.agent.role if task.agent else "None"
        print(f"   Task {i}: {task.description[:60]}...")
        print(f"      Agent: {agent_role}")
    
except Exception as e:
    print(f"❌ CRITICAL: Crew creation failed!")
    print(f"   Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# TEST 5: Test crew execution (DRY RUN)
print("\n5️⃣ CREW EXECUTION TEST (DRY RUN):")
print("-" * 80)

try:
    print("Testing PM crew kickoff (this may take 10-30 seconds)...")
    print("   If this hangs, agents are NOT executing tasks!")
    
    # Run with timeout
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Crew execution timeout!")
    
    # Set 60 second timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    result = pm_crew.kickoff()
    
    signal.alarm(0)  # Cancel timeout
    
    print(f"✅ PM Crew completed!")
    print(f"   Result type: {type(result)}")
    print(f"   Result: {str(result)[:200]}...")
    
except TimeoutError as e:
    print(f"❌ CRITICAL: Crew execution TIMEOUT!")
    print(f"   {e}")
    print(f"   This means agents are stuck!")
    sys.exit(1)
except Exception as e:
    print(f"❌ CRITICAL: Crew execution failed!")
    print(f"   Error: {e}")
    traceback.print_exc()
    sys.exit(1)

# TEST 6: Check tools
print("\n6️⃣ TOOL VERIFICATION:")
print("-" * 80)

try:
    from src.tools import (
        read_file_from_repo_tool,
        create_github_issue_tool,
        list_open_issues_tool,
        create_branch_tool,
        create_pull_request_tool,
    )
    
    print(f"✅ read_file_from_repo_tool: {type(read_file_from_repo_tool)}")
    print(f"✅ create_github_issue_tool: {type(create_github_issue_tool)}")
    print(f"✅ list_open_issues_tool: {type(list_open_issues_tool)}")
    print(f"✅ create_branch_tool: {type(create_branch_tool)}")
    print(f"✅ create_pull_request_tool: {type(create_pull_request_tool)}")
    
except ImportError as e:
    print(f"❌ CRITICAL: Tool import failed!")
    print(f"   Error: {e}")
    sys.exit(1)

# SUCCESS!
print("\n" + "=" * 80)
print("✅ ALL DIAGNOSTIC TESTS PASSED!")
print("=" * 80)
print("\nSystem is working correctly!")
print("If agents still don't work, check:")
print("  1. Telegram bot logs during execution")
print("  2. CrewAI verbose mode")
print("  3. GitHub API rate limits")
print("  4. Network connectivity")
