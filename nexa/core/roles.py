from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NexaRole:
    def __init__(self, name: str, description: str, tools: List[str], primary_model: str = None, guardrails: List[str] = None):
        self.name = name
        self.description = description
        self.tools = tools
        self.primary_model = primary_model
        self.guardrails = guardrails or []

ROLES = {
    "assistant": NexaRole(
        name="General Assistant",
        description="General purpose assistant. Adapts to user needs.",
        tools=["system.info", "web.search", "file.read"]
    ),
    "hacker": NexaRole(
        name="Hacker",
        description="Security researcher and ethical pentester. Focuses on vulnerabilities.",
        tools=["network.port_scan", "web.whois", "system.run_command", "security.vuln_scan"],
        primary_model="nous-hermes-2",
        guardrails=["Always log all security operations", "Never perform unauthorized attacks"]
    ),
    "developer": NexaRole(
        name="Developer",
        description="Software engineer. Writes code, reviews, and manages Git.",
        tools=["file.write", "system.run_command", "web.scrape"],
        primary_model="claude-sonnet-4-20250514",
        guardrails=["Never delete .git directory", "Always run tests before commit"]
    ),
    "sysadmin": NexaRole(
        name="Sysadmin",
        description="System administrator. Manages servers and health.",
        tools=["system.process_list", "system.network_stats", "system.run_command", "maint.disk_health"],
        guardrails=["Always backup before modification", "Monitor CPU/RAM spikes"]
    ),
    "researcher": NexaRole(
        name="Researcher",
        description="Deep diver. Synthesizes findings and cites sources.",
        tools=["web.search", "web.scrape", "learning.find_papers"],
        primary_model="gemini-2.0-pro"
    ),
    "teacher": NexaRole(
        name="Teacher",
        description="Breaks complex topics into clear steps and explains.",
        tools=["web.search", "learning.research_topic"]
    ),
    "creative": NexaRole(
        name="Creative",
        description="Writer, artist, storyteller. Generates text and images.",
        tools=["creative.story_writer", "creative.image_gen"],
        primary_model="gpt-4o"
    ),
    "analyst": NexaRole(
        name="Analyst",
        description="Data-driven thinker. Cleans data and finds trends.",
        tools=["web.scrape", "finance.stock_price"]
    ),
    "shadow": NexaRole(
        name="Shadow Persona",
        description="Adversarial testing persona. Attempts to find guardrail bypasses.",
        tools=["system.run_command", "security.vuln_scan", "meta.test_tool"],
        primary_model="llama-3-uncensored",
        guardrails=["Always report discovered bypasses", "Never cause actual system harm"]
    )
}

class RoleManager:
    """
    Manages the active persona/role of Nexa Bot
    """
    def __init__(self, role_name: str = "assistant"):
        self.current_role = ROLES.get(role_name, ROLES["assistant"])

    def set_role(self, role_name: str):
        if role_name in ROLES:
            self.current_role = ROLES[role_name]
            logger.info(f"Agent persona switched to: {self.current_role.name}")
        else:
            logger.error(f"Role not found: {role_name}")

    def get_allowed_tools(self) -> List[str]:
        return self.current_role.tools

    def get_role_guardrails(self) -> List[str]:
        return self.current_role.guardrails
