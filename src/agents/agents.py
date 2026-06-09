import asyncio
from agents.ai_model import upload_csv,collector_fetch_from_file,collector_fetch ,qualifier_analyze, json_to_csv_dynamic


class Collector:
    async def collect(self, task: str, source_file: str = None, source_hint: str = "") -> str:
        if source_file:
            # Step A: Upload (using thread because it's a network/disk IO)
            file_obj = await asyncio.to_thread(upload_csv, source_file)
            # Step B: Fetch using the file
            result = await asyncio.to_thread(collector_fetch_from_file, task, file_obj)
        else:
            # Fallback to your original text-based fetch
            result = await asyncio.to_thread(collector_fetch, task, source_hint)
            
        print(f"[Collector] Data gathered.")
        return result


class Qualifier:
    async def qualify(self, raw_data: str, criteria: str) -> str:
        print("[Qualifier] Analyzing and filtering data...")
        result = await asyncio.to_thread(qualifier_analyze, raw_data, criteria)
        print(result)
        return result


class Orchestrator:
    def __init__(self):
        self.collector = Collector()
        self.qualifier = Qualifier()

    async def run_pipeline(
        self,
        task: str,
        criteria: str,
        schema: list[str],
        source_hint: str = ""
    ) -> str:
        print("\n--- Orchestrator: starting pipeline ---")

        # Step 1: Collect
        raw_data = await self.collector.collect(task, source_hint=source_hint)

        # Step 2: Qualify
        qualified_data = await self.qualifier.qualify(raw_data, criteria)

        print("[System] Converting dynamic JSON schema to CSV...")
        final_csv = json_to_csv_dynamic(qualified_data)

        print("\n--- Orchestrator: pipeline complete ---")
        return final_csv