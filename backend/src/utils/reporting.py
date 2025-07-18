"""
Report generation utilities.
Moved from main.py to separate reporting logic.
Handles final report compilation and formatting.
"""
from datetime import datetime
from ..models.agent_state import AgentState

class ReportGenerator:
    """
    Utility class for generating final reports from agent execution results.
    Formats and compiles results from all agents into a comprehensive report.
    """
    
    def generate_final_report(self, state: AgentState) -> str:
        """Generate the final report after task completion"""
        task = state.query
        report_body = []

        if "research" in state.results:
            report_body.append("🔬 Research Findings:\n" + state.results["research"]["findings"])
        
        if "analysis" in state.results:
            report_body.append("📊 Analysis Insights:\n" + state.results["analysis"]["insights"])
        
        if "writing" in state.results:
            report_body.append("✍️ Final Written Content:\n" + state.results["writing"]["content"])
        
        if "review" in state.results:
            report_body.append("✅ Reviewer Assessment:\n" + state.results["review"]["assessment"])

        report = "\n\n".join(report_body) or "No output generated."
        
        final_report = f"""
                📄 FINAL REPORT
                {'='*50}
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                Task ID: {state.task_id}
                Topic: {task}
                Status: {state.status}
                {'='*50}

                {report}

                {'='*50}
                Agents Involved: {", ".join(state.completed_agents)}
                Errors: {state.errors if state.errors else "None"}
                Total Iterations: {state.iteration_count}
                Report compiled by Multi-Agent AI System powered by Groq
        """
        
        return final_report
