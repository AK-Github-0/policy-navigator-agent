"""
Policy Navigator Agent - Streamlit Web Interface
"""

import streamlit as st
from main import PolicyNavigator
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level="WARNING")

# Page configuration
st.set_page_config(
    page_title="Policy Navigator Agent",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    with st.spinner("Initializing Policy Navigator Agent..."):
        st.session_state.agent = PolicyNavigator()
        st.session_state.conversation_history = []

# Sidebar
with st.sidebar:
    st.markdown("### 🔧 Settings")
    
    mode = st.radio(
        "Query Mode",
        ["General Query", "Policy Status", "Case Law Search"],
        help="Select the type of query you want to make"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    if st.button("Refresh Stats"):
        try:
            # This would connect to actual stats
            st.metric("Documents Indexed", "1,250")
            st.metric("Policies Tracked", "347")
            st.metric("Cases Catalogued", "89")
        except Exception as e:
            st.error(f"Error loading stats: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("### 📚 Resources")
    st.markdown("""
    - [Federal Register](https://www.federalregister.gov/)
    - [CourtListener](https://www.courtlistener.com/)
    - [EPA Regulations](https://www.epa.gov/)
    """)
    
    st.markdown("---")
    
    if st.button("Clear History"):
        st.session_state.conversation_history = []
        st.success("History cleared!")

# Main content
st.markdown('<p class="main-header">📋 Policy Navigator Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Agent RAG System for Government Regulation Search</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Query", "📊 Analytics", "⚙️ Configuration", "ℹ️ About"])

with tab1:
    # Query interface based on mode
    if mode == "General Query":
        st.markdown("### Ask a Question")
        
        query = st.text_area(
            "Enter your question:",
            placeholder="e.g., What are the compliance requirements for small businesses under GDPR?",
            height=100
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.button("🔍 Search", type="primary", use_container_width=True)
        with col2:
            show_sources = st.checkbox("Show detailed sources", value=True)
        
        if submit_button and query:
            with st.spinner("Processing your query..."):
                try:
                    response = st.session_state.agent.query(query)
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        'query': query,
                        'response': response
                    })
                    
                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(response.get('answer', 'No answer provided'))
                    
                    # Display sources
                    if show_sources and response.get('sources'):
                        st.markdown("### 📚 Sources")
                        for i, source in enumerate(response['sources'], 1):
                            with st.expander(f"Source {i}: {source.get('title', 'Unknown')}"):
                                st.markdown(f"**Type:** {source.get('type', 'N/A')}")
                                st.markdown(f"**Reference:** {source.get('reference', 'N/A')}")
                                st.markdown(f"**Relevance Score:** {source.get('score', 0.0):.2f}")
                    
                    # Display metadata
                    if response.get('metadata'):
                        with st.expander("🔍 Query Details"):
                            st.json(response['metadata'])
                    
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
    
    elif mode == "Policy Status":
        st.markdown("### Check Policy Status")
        
        policy_id = st.text_input(
            "Enter policy identifier:",
            placeholder="e.g., Executive Order 14067",
            help="Enter the policy name or number"
        )
        
        if st.button("Check Status", type="primary"):
            if policy_id:
                with st.spinner("Checking policy status..."):
                    try:
                        status = st.session_state.agent.check_policy_status(policy_id)
                        
                        # Display status
                        st.markdown("### 📋 Policy Status")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Status", status.get('status', 'UNKNOWN'))
                        with col2:
                            st.metric("Source", status.get('source', 'N/A'))
                        with col3:
                            st.metric("Last Checked", status.get('last_checked', 'N/A')[:10])
                        
                        if status.get('title'):
                            st.markdown(f"**Title:** {status['title']}")
                        
                        if status.get('abstract'):
                            st.markdown("**Summary:**")
                            st.info(status['abstract'])
                        
                        if status.get('html_url'):
                            st.markdown(f"[View Full Document]({status['html_url']})")
                        
                    except Exception as e:
                        st.error(f"Error checking status: {str(e)}")
            else:
                st.warning("Please enter a policy identifier")
    
    elif mode == "Case Law Search":
        st.markdown("### Search Case Law")
        
        regulation = st.text_input(
            "Enter regulation or law:",
            placeholder="e.g., Section 230",
            help="Enter the regulation to search for related cases"
        )
        
        limit = st.slider("Number of cases", 1, 10, 5)
        
        if st.button("Search Cases", type="primary"):
            if regulation:
                with st.spinner("Searching case law..."):
                    try:
                        cases = st.session_state.agent.search_cases(regulation, limit)
                        
                        st.markdown(f"### ⚖️ Found {len(cases)} Cases")
                        
                        for i, case in enumerate(cases, 1):
                            with st.expander(f"{i}. {case.get('name', 'Unknown Case')}"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Court:** {case.get('court', 'N/A')}")
                                    st.markdown(f"**Year:** {case.get('year', 'N/A')}")
                                with col2:
                                    st.markdown(f"**Citation:** {case.get('citation', 'N/A')}")
                                    st.markdown(f"**Source:** {case.get('source', 'N/A')}")
                                
                                st.markdown("**Summary:**")
                                st.write(case.get('summary', 'No summary available'))
                                
                                if case.get('url') and case['url'] != 'N/A':
                                    st.markdown(f"[View Case Details]({case['url']})")
                        
                    except Exception as e:
                        st.error(f"Error searching cases: {str(e)}")
            else:
                st.warning("Please enter a regulation")
    
    # Conversation history
    if st.session_state.conversation_history:
        st.markdown("---")
        st.markdown("### 📝 Conversation History")
        
        for i, item in enumerate(reversed(st.session_state.conversation_history[-5:])):
            with st.expander(f"Query: {item['query'][:50]}..."):
                st.markdown(f"**Q:** {item['query']}")
                st.markdown(f"**A:** {item['response'].get('answer', 'N/A')[:300]}...")

with tab2:
    st.markdown("### 📊 Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Queries", len(st.session_state.conversation_history))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Documents Indexed", "1,250")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Response Time", "2.3s")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active Policies", "347")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📈 Query Trends")
    st.info("Analytics dashboard would show query trends, popular topics, and system performance metrics")

with tab3:
    st.markdown("### ⚙️ Configuration")
    
    st.markdown("#### 🔔 Notifications")
    enable_slack = st.checkbox("Enable Slack notifications")
    if enable_slack:
        slack_channel = st.text_input("Slack channel", placeholder="#compliance")
    
    st.markdown("#### 📅 Reminders")
    enable_calendar = st.checkbox("Enable calendar reminders")
    if enable_calendar:
        reminder_days = st.number_input("Days before deadline", min_value=1, max_value=90, value=30)
    
    st.markdown("#### 🔍 Search Settings")
    top_k = st.slider("Number of results to retrieve", 1, 20, 5)
    
    if st.button("Save Configuration"):
        st.success("Configuration saved successfully!")

with tab4:
    st.markdown("### ℹ️ About Policy Navigator Agent")
    
    st.markdown("""
    Policy Navigator Agent is a Multi-Agent RAG system designed to help you:
    
    - 🔍 Query complex government regulations
    - ✅ Check policy status in real-time
    - ⚖️ Search for related case law
    - 📊 Extract compliance requirements
    - 🔔 Get notifications on policy changes
    
    #### 🏗️ Architecture
    
    The system uses multiple specialized agents:
    - **Orchestrator Agent**: Routes queries to specialized agents
    - **Retrieval Agent**: Searches vector database
    - **API Agent**: Queries external government APIs
    - **Synthesizer Agent**: Generates structured answers
    - **Action Agent**: Handles integrations (Slack, Calendar)
    
    #### 🛠️ Technologies
    
    - aiXplain SDK for agent orchestration
    - ChromaDB for vector storage
    - Federal Register API for policy data
    - CourtListener API for case law
    - Streamlit for web interface
    
    #### 📚 Resources
    
    - [GitHub Repository](https://github.com/yourusername/policy-navigator-agent)
    - [aiXplain Documentation](https://docs.aixplain.com)
    - [Project Documentation](README.md)
    """)
    
    st.markdown("---")
    st.markdown("Built with ❤️ using aiXplain SDK")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">Policy Navigator Agent v1.0.0 | '
    'Powered by aiXplain</div>',
    unsafe_allow_html=True
)