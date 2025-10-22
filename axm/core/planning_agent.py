"""Planning Agent for task decomposition and execution"""

from typing import Any, Dict, List

from pydantic import BaseModel

from axm.core.agent import Agent
from axm.core.types import Plan, Task


class PlanningAgent(Agent):
    """
    An agent that can break down complex tasks into steps and execute them.

    Example:
        agent = PlanningAgent("gpt-4")
        result = agent.execute_plan("Research AI trends and write a summary")
    """

    def create_plan(self, goal: str) -> Plan:
        """
        Create an execution plan for a given goal.

        Args:
            goal: The high-level goal to accomplish

        Returns:
            A Plan object with tasks
        """

        class PlanSchema(BaseModel):
            tasks: List[Dict[str, Any]]

        system_prompt = """You are a planning expert. Break down user goals into clear, actionable tasks.
Each task should have:
- id: unique identifier (task_1, task_2, etc.)
- description: what needs to be done
- dependencies: list of task IDs that must complete first (empty list if none)

Return a JSON object with a 'tasks' array."""

        # Temporarily override system prompt
        original_messages = self.memory.messages.copy()
        self.reset()
        self.memory.add_message({"role": "system", "content": system_prompt})

        prompt = f"Create a step-by-step plan to accomplish this goal: {goal}"

        plan_data = self.run(prompt, response_format=PlanSchema)

        # Restore original messages
        self.memory.messages = original_messages

        # Create Task objects
        tasks = []
        if isinstance(plan_data, PlanSchema):
            for task_dict in plan_data.tasks:
                tasks.append(
                    Task(
                        id=task_dict.get("id", f"task_{len(tasks) + 1}"),
                        description=task_dict["description"],
                        dependencies=task_dict.get("dependencies", []),
                    )
                )

        return Plan(goal=goal, tasks=tasks)

    def execute_task(self, task: Task) -> str:
        """Execute a single task"""
        task.status = "in_progress"

        try:
            result = self.run(
                f"Execute this task: {task.description}\n\nProvide a clear, concise result."
            )
            task.status = "completed"
            task.result = result
            return result
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            raise

    def execute_plan(self, goal: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Create and execute a plan for a goal.

        Args:
            goal: The high-level goal to accomplish
            verbose: Whether to print progress

        Returns:
            Dictionary with plan results
        """
        if verbose:
            print(f"🎯 Goal: {goal}\n")

        # Create the plan
        plan = self.create_plan(goal)

        if verbose:
            print(f"📋 Created plan with {len(plan.tasks)} tasks:\n")
            for i, task in enumerate(plan.tasks, 1):
                deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
                print(f"  {i}. {task.description}{deps}")
            print()

        # Execute tasks in order (respecting dependencies)
        results = {}
        executed_tasks = set()

        while not plan.is_complete:
            # Find next executable task (no pending dependencies)
            for task in plan.tasks:
                if task.status != "pending":
                    continue

                # Check if all dependencies are met
                deps_met = all(dep in executed_tasks for dep in task.dependencies)

                if deps_met:
                    if verbose:
                        print(f"⚙️  Executing: {task.description}")

                    try:
                        result = self.execute_task(task)
                        results[task.id] = result
                        executed_tasks.add(task.id)

                        if verbose:
                            print(f"✅ Completed: {task.description}")
                            result_preview = (
                                f"   Result: {result[:100]}...\n"
                                if len(result) > 100
                                else f"   Result: {result}\n"
                            )
                            print(result_preview)
                    except Exception as e:
                        if verbose:
                            print(f"❌ Failed: {task.description}")
                            print(f"   Error: {str(e)}\n")
                        # Break if a task fails
                        break

            # Check for deadlock (no tasks can be executed)
            pending_tasks = [t for t in plan.tasks if t.status == "pending"]
            if pending_tasks:
                # Check if any pending task has its dependencies met
                can_execute = any(
                    all(dep in executed_tasks for dep in task.dependencies)
                    for task in pending_tasks
                )
                if not can_execute:
                    if verbose:
                        print("⚠️  Cannot continue: circular dependency or failed task")
                    break

        # Prepare summary
        completed = sum(1 for t in plan.tasks if t.status == "completed")
        failed = sum(1 for t in plan.tasks if t.status == "failed")

        if verbose:
            print(f"\n📊 Summary: {completed}/{len(plan.tasks)} tasks completed, {failed} failed")

        return {
            "goal": goal,
            "plan": plan,
            "results": results,
            "completed": completed,
            "failed": failed,
            "success": plan.is_complete,
        }
