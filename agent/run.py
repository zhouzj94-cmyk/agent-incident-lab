import asyncio
import argparse
from pathlib import Path

from environment.incident_env import IncidentEnvironment
from providers.ollama import OllamaProvider
from tools.registry import ToolRegistry
from tools.search_logs import SearchLogsTool
from tools.error_stats import GetErrorStatsTool
from tools.compare_window import CompareWindowTool
from tools.related_events import GetRelatedEventsTool
from tools.service_summary import GetServiceSummaryTool
from tools.verifier import VerifyHypothesisTool
from tools.finish import FinishInvestigationTool
from agent.controller import InvestigationController


async def run_investigation(incident_id: str, data_path: str, max_steps: int = 12):
    env = IncidentEnvironment(data_path)
    env.initialize()

    incident = env.get_incident(incident_id)
    if not incident:
        print(f"Incident {incident_id} not found")
        return

    llm = OllamaProvider()

    tools = ToolRegistry()
    tools.register(SearchLogsTool(env.log_store))
    tools.register(GetErrorStatsTool(env.log_store))
    tools.register(CompareWindowTool(env.log_store))
    tools.register(GetRelatedEventsTool(env.log_store))
    tools.register(GetServiceSummaryTool(env.log_store))
    tools.register(VerifyHypothesisTool(env.log_store._events))
    tools.register(FinishInvestigationTool())

    controller = InvestigationController(
        llm=llm,
        tools=tools,
        max_steps=max_steps,
    )

    result = await controller.investigate(incident)

    print(f"\nInvestigation Complete")
    print(f"Incident: {result['incident_id']}")
    print(f"Steps: {result['steps']}")
    print(f"\nFinal Answer:")
    print(result['final_answer'])

    await llm.close()

    return result


def main():
    parser = argparse.ArgumentParser(description="Run incident investigation")
    parser.add_argument("--incident", required=True, help="Incident ID")
    parser.add_argument("--data", default="data", help="Data directory path")
    parser.add_argument("--max-steps", type=int, default=12, help="Maximum investigation steps")

    args = parser.parse_args()

    asyncio.run(run_investigation(args.incident, args.data, args.max_steps))


if __name__ == "__main__":
    main()
