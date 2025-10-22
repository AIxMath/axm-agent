"""Multi-Agent system for collaboration"""

from typing import Dict, List, Optional

from axm.core.agent import Agent


class MultiAgent:
    """
    System for managing multiple agents working together.

    Example:
        researcher = Agent("gpt-4", role="researcher")
        writer = Agent("gpt-4", role="writer")
        team = MultiAgent([researcher, writer])
        result = team.collaborate("Write an article about AI")
    """

    def __init__(self, agents: List[Agent], orchestrator_model: str = "gpt-4"):
        """
        Initialize a multi-agent system.

        Args:
            agents: List of agents to collaborate
            orchestrator_model: Model for the orchestrator
        """
        self.agents = {agent.config.role or f"agent_{i}": agent for i, agent in enumerate(agents)}
        self.orchestrator = Agent(
            orchestrator_model,
            system_prompt=self._create_orchestrator_prompt(),
        )

    def _create_orchestrator_prompt(self) -> str:
        """Create system prompt for orchestrator"""
        roles = ", ".join(self.agents.keys())
        return f"""You are an orchestrator managing a team of agents with these roles: {roles}.

Your job is to:
1. Break down the user's request into subtasks
2. Assign each subtask to the most appropriate agent
3. Coordinate the agents' work
4. Synthesize their outputs into a final response

For each subtask, specify which agent should handle it and what they should do."""

    def collaborate(self, task: str, max_rounds: int = 3, verbose: bool = True) -> str:
        """
        Have agents collaborate on a task.

        Args:
            task: The task to accomplish
            max_rounds: Maximum collaboration rounds
            verbose: Whether to print progress

        Returns:
            Final collaborative result
        """
        if verbose:
            print(f"🤝 Starting collaboration on: {task}\n")

        conversation_history: List[Dict[str, str]] = []

        for round_num in range(max_rounds):
            if verbose:
                print(f"📍 Round {round_num + 1}/{max_rounds}")

            # Orchestrator decides what to do
            orchestrator_prompt = f"""Task: {task}

Previous work:
{self._format_history(conversation_history)}

What should we do next? Assign work to agents or provide final answer.
If providing final answer, start with "FINAL:".
Otherwise, format as: ASSIGN <agent_role>: <instruction>"""

            orchestrator_response: str = self.orchestrator.run(orchestrator_prompt)

            if verbose:
                print(f"🎯 Orchestrator: {orchestrator_response[:100]}...\n")

            # Check if we have a final answer
            if orchestrator_response.startswith("FINAL:"):
                final_answer = orchestrator_response[6:].strip()
                if verbose:
                    print("✅ Final result achieved!\n")
                return final_answer

            # Parse agent assignments
            assignments = self._parse_assignments(str(orchestrator_response))

            # Execute assignments
            for agent_role, instruction in assignments.items():
                if agent_role in self.agents:
                    if verbose:
                        print(f"  👤 {agent_role}: {instruction[:80]}...")

                    agent = self.agents[agent_role]
                    result = agent.run(instruction)

                    conversation_history.append(
                        {"role": agent_role, "instruction": instruction, "result": result}
                    )

                    if verbose:
                        print(f"     ✓ {result[:80]}...\n")

        # If we exhausted rounds, ask orchestrator for final synthesis
        if verbose:
            print("⏱️  Max rounds reached, synthesizing final answer...\n")

        final_prompt = f"""Task: {task}

All work completed:
{self._format_history(conversation_history)}

Provide a comprehensive final answer synthesizing all the work."""

        final_answer: str = self.orchestrator.run(final_prompt)
        return final_answer

    def _parse_assignments(self, response: str) -> Dict[str, str]:
        """Parse agent assignments from orchestrator response"""
        assignments = {}
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("ASSIGN"):
                # Format: ASSIGN agent_role: instruction
                parts = line[6:].split(":", 1)
                if len(parts) == 2:
                    role = parts[0].strip()
                    instruction = parts[1].strip()
                    assignments[role] = instruction
        return assignments

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history"""
        if not history:
            return "No previous work."

        formatted = []
        for entry in history:
            formatted.append(
                f"- {entry['role']}: {entry['instruction']}\n  Result: {entry['result']}"
            )
        return "\n".join(formatted)

    def add_agent(self, agent: Agent, role: Optional[str] = None) -> None:
        """Add an agent to the team"""
        agent_role = role or agent.config.role or f"agent_{len(self.agents)}"
        self.agents[agent_role] = agent

    def get_agent(self, role: str) -> Optional[Agent]:
        """Get an agent by role"""
        return self.agents.get(role)
