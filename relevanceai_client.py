from textwrap import dedent
import asyncio
from dotenv import load_dotenv
from relevanceai import RelevanceAI

load_dotenv()

class RelevanceAIClient:
    def __init__(self):
        self.client = RelevanceAI()
        self.agent_id = "3589277c-16aa-4ddc-8c8f-035f29a6a94b"  # prospect research agent

    async def research_prospect(self, person_name, company_name, website):
        message = dedent(f"""
        Research the following prospect:
        {person_name}
        {company_name}
        {website}
        """)

        task = self.client.tasks.trigger_task(
            agent_id=self.agent_id,
            message=message
        )

        while not self.client.tasks.get_task_output_preview(self.agent_id, task.conversation_id):
            await asyncio.sleep(5)

        task_output = self.client.tasks.get_task_output_preview(
            self.agent_id, task.conversation_id)
        return task_output["answer"]

relevanceai_client = RelevanceAIClient()