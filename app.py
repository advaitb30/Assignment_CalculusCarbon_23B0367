"""
Streamlit Chatbot Interface - Phase 3
AI Assistant for Calculus Carbon Deal Team
"""

import streamlit as st
from data_loader import DataLoader
from query_engine import QueryEngine
from llm_interface import LLMInterface
import json

# Page config
st.set_page_config(
    page_title="Calculus Carbon AI Assistant",
    page_icon="🌱",
    layout="wide"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.messages = []

# Load data (once)
@st.cache_resource
def load_system():
    """Load data and initialize systems"""
    data = DataLoader().load_all()
    query_engine = QueryEngine(data)
    query_engine.init_semantic_search()
    llm = LLMInterface()
    return data, query_engine, llm

# UI Header
st.title("🌱 Calculus Carbon AI Assistant")
st.markdown("*Your intelligent deal team companion for NbS investments*")

# Sidebar with sample queries
with st.sidebar:
    st.header("📋 Sample Questions")
    
    sample_queries = {
        "Developers in Latin America": "Which developers have ARR projects in Latin America?",
        "Match Investors to Project": "Which investors match the sector and ticket size of Project P001?",
        "Communications Summary": "Summarize all communication related to VerdeNova",
        "Meeting Actionables": "What were the actionables from the last meeting with NorthStar?"
    }
    
    st.markdown("**Quick Start:**")
    for label, query in sample_queries.items():
        if st.button(label, key=f"sample_{label}"):
            st.session_state.selected_query = query
    
    st.markdown("---")
    st.markdown("**Data Loaded:**")
    
    if st.button("🔄 Reload Data"):
        st.cache_resource.clear()
        st.rerun()

# Load system
try:
    data, query_engine, llm = load_system()
    st.session_state.data_loaded = True
    
    # Show data stats in sidebar
    with st.sidebar:
        st.metric("Entities", len(data.entities))
        st.metric("Projects", len(data.projects))
        st.metric("Communications", len(data.communications))
        st.metric("Relationships", len(data.relationships))
        
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Chat interface
st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle sample query selection
if 'selected_query' in st.session_state:
    user_input = st.session_state.selected_query
    del st.session_state.selected_query
else:
    user_input = st.chat_input("Ask me anything about projects, investors, or communications...")

# Process user input
if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Process query
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching data..."):
            
            # Determine query type and execute
            query_lower = user_input.lower()
            
            try:
                # Query 1: Developers by region and type
                if "arr" in query_lower and ("latin america" in query_lower or "latam" in query_lower):
                    regions = ['Brazil', 'Peru', 'Mexico', 'Argentina', 'Colombia']
                    results = query_engine.query_developers_by_region_and_type('ARR', regions)
                    response = llm.generate_response(user_input, results, 'developers_by_region')
                
                # Query 2: Match investors to project
                elif "match" in query_lower or ("investor" in query_lower and "project" in query_lower):
                    # Extract project ID
                    import re
                    project_match = re.search(r'P\d{3}', user_input, re.IGNORECASE)
                    if project_match:
                        project_id = project_match.group(0).upper()
                        results = query_engine.query_matching_investors(project_id)
                        response = llm.generate_response(user_input, results, 'matching_investors')
                    else:
                        response = "Please specify a project ID (e.g., P001, P002)."
                
                # Query 3: Summarize communications
                elif "summarize" in query_lower or "communication" in query_lower:
                    # Extract entity name
                    words = user_input.split()
                    entity_name = None
                    for i, word in enumerate(words):
                        if word.lower() in ['about', 'related', 'regarding', 'for']:
                            if i + 1 < len(words):
                                entity_name = words[i + 1]
                                break
                    
                    if entity_name:
                        results = query_engine.summarize_communications(entity_name)
                        response = llm.generate_response(user_input, results, 'communications_summary')
                    else:
                        response = "Please specify an entity name (e.g., VerdeNova, NorthStar)."
                
                # Query 4: Meeting actionables
                elif "actionable" in query_lower or "meeting" in query_lower:
                    # Extract entity name
                    words = user_input.split()
                    entity_name = None
                    for i, word in enumerate(words):
                        if word.lower() in ['with', 'about']:
                            if i + 1 < len(words):
                                entity_name = words[i + 1].rstrip('?')
                                break
                    
                    if entity_name:
                        results = query_engine.find_actionables_from_meeting(entity_name)
                        if results:
                            # Use specialized actionables extraction
                            actionables = llm.extract_actionables(results['transcript_text'])
                            response = f"**Meeting with {results['entity']['canonical_name']}**\n\n{actionables}"
                        else:
                            response = f"No meeting transcripts found for {entity_name}."
                    else:
                        response = "Please specify an entity name (e.g., NorthStar, VerdeNova)."
                
                # Fallback: Semantic search
                else:
                    results = query_engine.semantic_search_communications(user_input, top_k=3)
                    response = llm.generate_response(user_input, results, 'semantic_search')
                
                # Display response
                st.markdown(response)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Error processing query: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>Calculus Carbon AI Assistant | Powered by Groq | Data as of October 2025</small>
</div>
""", unsafe_allow_html=True)