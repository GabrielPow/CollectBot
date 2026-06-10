import streamlit as st
import asyncio
import os
import pandas as pd
from io import StringIO
from agents.agents import Orchestrator

# 1. Page Configuration
st.set_page_config(page_title="AI Data Pipeline Bot", page_icon="🤖", layout="wide")
st.title("🤖 CollectBot - AI Data Collector")
st.caption("Upload a CSV dataset, define your criteria, and let the agents structure it.")

# 2. Initialize Orchestrator in session state so it persists
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator()

# 3. Sidebar for Configuration
with st.sidebar:
    st.header("Pipeline Configuration")
    
    task_input = st.text_area(
        "1. What data should the Collector fetch?",
        placeholder="Extract records of countries making significant shifts toward low-carbon options.",
        help="Instruct the collection agent on what to look for."
    )
    
    criteria_input = st.text_area(
        "2. What are the Qualification criteria?",
        placeholder="Must have a renewable energy share greater than 20% or notable increases in solar/wind generation. Assign relevance based on their progress scale.",
        help="The filter criteria used by the Qualifier agent."
    )

    formatting_suggestions = st.text_area(
        "3.. Optional Formatting Suggestions (Leave blank to keep default layout)",
        placeholder="Example: Rename columns to uppercase, or append '%' to numerical shares..."
    )

# 4. Main Panel: File Upload
uploaded_file = st.file_uploader("Upload your source CSV file", type=["csv"])

if uploaded_file is not None:
    st.success(f"📂 Loaded: {uploaded_file.name}")
    
    # Optional: Preview the raw file so the user knows it read correctly
    with st.expander("Preview Raw Uploaded Data"):
        df_preview = pd.read_csv(uploaded_file)
        st.dataframe(df_preview.head(10))

    # 5. Execution Button
    
    if st.button("Run Pipeline 🚀", type="primary"):
        # Create a temporary file on disk because Gemini Files API requires a path
        temp_dir = "tmp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # UI Status containers to show real-time progress
        with st.status("Executing Agent Pipeline...", expanded=True) as status:
            try:
                st.write("🏃 Running Orchestrator...")
                
                # Run the async pipeline safely within Streamlit's sync environment
                final_csv_output = asyncio.run(
                    st.session_state.orchestrator.run_pipeline(
                        task=task_input,
                        criteria=criteria_input,
                        source_hint=temp_file_path,
                        formatting_suggestions=formatting_suggestions
                    )
                )
                
                status.update(label="Pipeline Complete!", state="complete", expanded=False)
                
                # 6. Display & Download Results
                st.subheader("📊 Final Formatted Output")
                
                # Convert the AI's CSV string output into a Pandas Dataframe for clean UI rendering
                try:
                    # Stripping any conversational agent tags if they leaked through
                    clean_csv = final_csv_output.replace("[Formatter]", "").strip()
                    result_df = pd.read_csv(StringIO(clean_csv))
                    
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Provide an immediate download button for the user
                    st.download_button(
                        label="Download Structured CSV",
                        data=clean_csv,
                        file_name="pipeline_output.csv",
                        mime="text/csv"
                    )
                except Exception as parse_err:
                    st.error("Failed to parse the AI output into a table format.")
                    st.code(final_csv_output)
                    
            except Exception as e:
                status.update(label="Pipeline Failed!", state="error")
                st.error(f"An error occurred: {e}")
                
            finally:
                # Cleanup: Always remove the temporary file from local storage
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
else:
    st.info("💡 Please upload a CSV file in the main panel to begin.")