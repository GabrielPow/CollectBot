import asyncio
import pandas as pd
from datetime import datetime
from io import StringIO
from agents.agents import Orchestrator

async def main():
    orchestrator = Orchestrator()
    result = await orchestrator.run_pipeline(
        task="Find all solar energy projects in California",
        criteria="Must be active and have a capacity > 50MW",
        schema=["project_name", "location", "capacity_mw", "status"],
        source_file="energy_data_2026.csv"  # The local path to your file
    )
    print(result)
    result

async def run_and_save_pipeline(task, criteria, schema, source_file_path):
    orchestrator = Orchestrator()
    # 1. Run your existing pipeline
    final_csv_text = await orchestrator.run_pipeline(task, criteria, schema, source_file_path)
    
    # 2. Generate a clean, unique output filename
    base_name = source_file_path.split(".csv")[0]  # e.g., "energy_data"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{base_name}_structured_{timestamp}.csv"
    
    # 3. Save it to an output directory
    clean_data = final_csv_text.replace("[Formatter]", "").strip()
    df = pd.read_csv(StringIO(clean_data))
    df.to_csv(output_filename, index=False)
    
    print(f"[System] Success! Cleaned dataset saved to: {output_filename}")
    return output_filename

asyncio.run(run_and_save_pipeline(
    task="Extract records of countries making significant shifts toward low-carbon options.", 
    criteria="Must have a renewable energy share greater than 20% or notable increases in solar/wind generation. Assign relevance based on their progress scale.", 
    schema=["country", "year", "renewable_share_percent", "fossil_fuel_twh"], 
    source_file_path="test_sample.csv"))