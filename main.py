import streamlit as st
from airtable_client import airtable_client
from relevanceai_client import relevanceai_client
import asyncio
import pandas as pd

TOOL_ICON = "🎯"
TOOL_NAME = "Research Qualification"
TOOL_DESCRIPTION = "Automate the sales qualification process with AI research agents"

st.set_page_config(
    page_title=f"{TOOL_NAME}",
    page_icon=f"{TOOL_ICON}",
)

st.markdown("""
    <style>
        [data-testid="stDecoration"] {
            display: none;
        }
    </style>""",
    unsafe_allow_html=True
)

if "has_output" not in st.session_state:
    st.session_state["has_output"] = False
    
if "batch_progress" not in st.session_state:
    st.session_state["batch_progress"] = None
    
def save_to_airtable(data):
    formatted_data = {
        "person_name": data["person_name"],
        "company_name": data["company_name"],
        "website_url": data["website"],
        "status": "In progress" 
    }
    return airtable_client.create(formatted_data, "contacts")

def update_airtable_with_research(record_id, data):
    return airtable_client.update(record_id, data, "contacts")


with st.container(border=True): 
    st.title(f"{TOOL_ICON} {TOOL_NAME}")
    st.write(f"{TOOL_DESCRIPTION}")
    st.text("")
    
    # Create tabs for single and batch processing
    tab1, tab2 = st.tabs(["Single Prospect", "Batch Upload"])
    
    with tab1:

        # User inputs with placeholder values
        person_name = st.text_input("**Person Name**", placeholder="John Doe")
        company_name = st.text_input("**Company Name**", placeholder="Acme Corporation")
        website = st.text_input("**Website**", placeholder="https://www.example.com")
        mock_true = st.toggle("Mock True", value=False)
        

        # Run tool
        st.info("👆 Fill in the options above to get started")
        if st.button("▶️ Run tool", use_container_width=True):
            with st.spinner("Saving contact and conducting research..."):
                # Collect form data
                form_data = {
                    "person_name": person_name,
                    "company_name": company_name,
                    "website": website
                }
                
                try:
                    # Save to Airtable
                    record = save_to_airtable(form_data)

                    research_output = asyncio.run(
                        relevanceai_client.research_prospect(
                            person_name,
                            company_name,
                            website
                        )
                    )
                    
                    update_airtable_with_research(record["id"], {"relevanceai_output": research_output, "status": "Complete"})
                    st.success("Research completed and saved!")
                    
                    st.session_state["has_output"] = True
                    st.session_state["research_output"] = research_output
                    
                except Exception as e:
                    # Only update status if record was created
                    if 'record' in locals():
                        airtable_client.update(record["id"], {"status": "Error"}, "contacts")
                    st.error(f"Error: {str(e)}")
                    
    with tab2:
        
        st.write("**Batch Upload**")
        st.info("Upload a CSV file with columns: person_name, company_name, website")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        mock_true_batch = st.toggle("Mock True (Batch)", value=False)
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.dataframe(df.head())
                
                if st.button("▶️ Process Batch", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for index, row in df.iterrows():
                        progress = (index + 1) / len(df)
                        status_text.text(f"Processing {index + 1} of {len(df)}: {row['person_name']}")
                        
                        try:
                            # Save to Airtable
                            form_data = {
                                "person_name": row['person_name'],
                                "company_name": row['company_name'],
                                "website": row['website']
                            }
                            record = save_to_airtable(form_data)
                            
                            research_output = asyncio.run(
                                relevanceai_client.research_prospect(
                                    row['person_name'],
                                    row['company_name'],
                                    row['website']
                                )
                            )

                            
                            update_airtable_with_research(record["id"], 
                                {"relevanceai_output": research_output, "status": "Complete"})
                            
                        except Exception as e:
                            if 'record' in locals():
                                airtable_client.update(record["id"], {"status": "Error"}, "contacts")
                            st.error(f"Error processing {row['person_name']}: {str(e)}")
                        
                        progress_bar.progress(progress)
                    
                    status_text.text("Batch processing complete!")
                    
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")


if st.session_state["has_output"]:
    with st.container(border=True):
        st.write("**Tool outputs**")
        st.write(st.session_state["research_output"])


    


