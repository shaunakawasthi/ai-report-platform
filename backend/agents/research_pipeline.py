from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================================
# STATE DEFINITION
# This is the shared whiteboard all agents read and write to.
# TypedDict means every key has a defined type — no surprises.
# ============================================================

class ReportState(TypedDict):
    topic: str                    # the original topic from the user
    research: str                 # raw research gathered by Research Agent
    analysis: str                 # insights extracted by Analysis Agent
    report_draft: str             # report written by Writing Agent
    validation_feedback: str      # feedback from Validator Agent
    final_report: str             # approved final report
    iteration_count: int          # how many times we've revised
    is_approved: bool             # whether validator approved the report

# ============================================================
# LLM SETUP
# One shared LLM instance used by all agents.
# Each agent gets different behavior via system prompts, not different models.
# ============================================================

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.3
)

# ============================================================
# AGENT 1 — RESEARCH AGENT
# Job: gather comprehensive information on the topic
# Input from state: topic
# Output to state: research
# ============================================================

async def research_agent(state: ReportState) -> ReportState:
    print(f"🔍 Research Agent working on: {state['topic']}")
    
    response = await llm.ainvoke([
        {
            "role": "system",
            "content": """You are an expert research specialist. 
            Your job is to gather comprehensive, factual information on any topic.
            Structure your research as:
            - Background and context
            - Current state and recent developments  
            - Key statistics and data points
            - Major challenges and opportunities
            - Key players and stakeholders
            Be thorough and factual. This research will be used by an analyst."""
        },
        {
            "role": "user",
            "content": f"Research this topic thoroughly: {state['topic']}"
        }
    ])
    
    # Update state with research results
    return {**state, "research": response.content}

# ============================================================
# AGENT 2 — ANALYSIS AGENT
# Job: analyze the research and extract meaningful insights
# Input from state: topic + research
# Output to state: analysis
# ============================================================

async def analysis_agent(state: ReportState) -> ReportState:
    print(f"🧠 Analysis Agent analyzing research...")
    
    response = await llm.ainvoke([
        {
            "role": "system",
            "content": """You are an expert analyst. 
            Your job is to analyze raw research and extract meaningful insights.
            Structure your analysis as:
            - Key themes and patterns
            - Critical insights and findings
            - Cause and effect relationships
            - Strategic implications
            - Areas of uncertainty or debate
            Be analytical and insightful. Avoid repeating raw facts — interpret them."""
        },
        {
            "role": "user",
            "content": f"""Analyze this research on {state['topic']}:
            
            {state['research']}
            
            Extract the most important insights and implications."""
        }
    ])
    
    return {**state, "analysis": response.content}

# ============================================================
# AGENT 3 — WRITING AGENT
# Job: write a professional structured report
# Input from state: topic + research + analysis
# Output to state: report_draft
# ============================================================

async def writing_agent(state: ReportState) -> ReportState:
    print(f"✍️ Writing Agent drafting report...")
    
    response = await llm.ainvoke([
        {
            "role": "system",
            "content": """You are an expert report writer.
            Your job is to write clear, professional, well-structured reports.
            Always structure reports as:
            1. Executive Summary (3-4 sentences)
            2. Introduction
            3. Key Findings (with subsections)
            4. Detailed Analysis
            5. Implications and Recommendations
            6. Conclusion
            Write in professional business language. Be clear and concise."""
        },
        {
            "role": "user",
            "content": f"""Write a professional report on: {state['topic']}
            
            Use this research:
            {state['research']}
            
            And this analysis:
            {state['analysis']}
            
            Produce a comprehensive, well-structured report."""
        }
    ])
    
    return {**state, "report_draft": response.content}

# ============================================================
# AGENT 4 — VALIDATOR AGENT
# Job: review the report quality and approve or request revision
# Input from state: topic + report_draft
# Output to state: validation_feedback + is_approved
# ============================================================

async def validator_agent(state: ReportState) -> ReportState:
    print(f"✅ Validator Agent reviewing report...")
    
    response = await llm.ainvoke([
        {
            "role": "system",
            "content": """You are a strict quality reviewer for research reports.
            Evaluate reports on:
            - Completeness (does it cover the topic thoroughly?)
            - Structure (is it well organized?)
            - Clarity (is it easy to understand?)
            - Accuracy (does it seem factually sound?)
            - Professional quality (is it ready for business use?)
            
            Respond in this exact format:
            APPROVED: [YES or NO]
            FEEDBACK: [your detailed feedback]
            
            Be strict — only approve truly high quality reports."""
        },
        {
            "role": "user",
            "content": f"""Review this report on {state['topic']}:
            
            {state['report_draft']}
            
            Is this report high quality and ready for use?"""
        }
    ])
    
    feedback = response.content
    is_approved = "APPROVED: YES" in feedback
    
    return {
        **state,
        "validation_feedback": feedback,
        "is_approved": is_approved,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

# ============================================================
# CONDITIONAL EDGE FUNCTION
# This decides what happens after validation.
# If approved → end the pipeline
# If not approved AND under 3 attempts → revise
# If not approved AND 3 attempts → end anyway (prevent infinite loop)
# ============================================================

def should_continue(state: ReportState) -> str:
    if state["is_approved"]:
        print(f"✅ Report approved after {state['iteration_count']} iteration(s)")
        return "approved"
    elif state["iteration_count"] >= 3:
        print(f"⚠️ Max iterations reached, using best draft")
        return "approved"
    else:
        print(f"🔄 Revision needed, iteration {state['iteration_count']}")
        return "revise"

# ============================================================
# FINALIZE FUNCTION
# Sets the final_report from the approved draft
# ============================================================

async def finalize_report(state: ReportState) -> ReportState:
    return {**state, "final_report": state["report_draft"]}

# ============================================================
# BUILD THE GRAPH
# This is where we wire everything together
# ============================================================

def build_research_pipeline():
    # Create the graph with our state definition
    graph = StateGraph(ReportState)
    
    # Add nodes — each node is an agent function
    graph.add_node("research", research_agent)
    graph.add_node("analysis", analysis_agent)
    graph.add_node("writing", writing_agent)
    graph.add_node("validation", validator_agent)
    graph.add_node("finalize", finalize_report)
    
    # Add edges — define the flow between nodes
    graph.set_entry_point("research")        # start here
    graph.add_edge("research", "analysis")   # research → analysis
    graph.add_edge("analysis", "writing")    # analysis → writing
    graph.add_edge("writing", "validation")  # writing

    graph.add_conditional_edges(
        "validation",
        should_continue,
        {
            "approved": "finalize",
            "revise": "writing"
        }
    )
    
    graph.add_edge("finalize", END)
    
    # THIS LINE IS MISSING — add it
    return graph.compile()

# Create one pipeline instance to reuse
research_pipeline = build_research_pipeline()

# ============================================================
# MAIN ENTRY FUNCTION
# This is what your API will call
# ============================================================

async def run_research_pipeline(topic: str) -> dict:
    """
    Runs the complete multi-agent research pipeline.
    Returns the final report and metadata.
    """
    
    # Initial state — only topic is set, everything else is empty
    initial_state = {
        "topic": topic,
        "research": "",
        "analysis": "",
        "report_draft": "",
        "validation_feedback": "",
        "final_report": "",
        "iteration_count": 0,
        "is_approved": False
    }
    
    # Run the pipeline
    final_state = await research_pipeline.ainvoke(initial_state)
    
    return {
        "final_report": final_state["final_report"],
        "iterations": final_state["iteration_count"],
        "approved": final_state["is_approved"],
        "validation_feedback": final_state["validation_feedback"]
    } 