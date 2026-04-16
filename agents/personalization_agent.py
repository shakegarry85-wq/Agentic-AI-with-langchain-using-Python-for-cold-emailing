"""
Personalization Agent for building detailed prospect profiles.
Uses LangChain to analyze research data and create personalized profiles.
"""

import logging
from typing import Dict, Any, Optional
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from prompts.personalization_prompt import PersonalizationPrompts

logger = logging.getLogger(__name__)

class PersonalizationAgent:
    """Agent responsible for creating personalized prospect profiles."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)

        # Initialize tools for the agent
        self.tools = [
            Tool(
                name="ProspectProfileBuilder",
                func=self._build_prospect_profile_wrapper,
                description="Build a detailed prospect profile from research data. Input should be research data in text format."
            ),
            Tool(
                name="PainPointAnalyzer",
                func=self._analyze_pain_points_wrapper,
                description="Analyze likely pain points for a prospect based on their role and company. Input should be prospect information."
            ),
            Tool(
                name="ValueAlignmentAnalyzer",
                func=self._analyze_value_alignment_wrapper,
                description="Analyze how our solution aligns with prospect needs. Input should be prospect profile and solution details."
            )
        ]

        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize the agent
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )

        logger.info("Personalization Agent initialized")

    def _build_prospect_profile_wrapper(self, query: str) -> str:
        """Wrapper for prospect profile building."""
        try:
            # In a full implementation, this would parse structured research data
            # For now, we'll treat the query as the research data
            research_data = query.strip()

            # Use LLM to build profile
            prompt = PersonalizationPrompts.get_prospect_profile_prompt()
            formatted_prompt = prompt.format(research_data=research_data)

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error building prospect profile: {str(e)}")
            return f"Error building prospect profile: {str(e)}"

    def _analyze_pain_points_wrapper(self, query: str) -> str:
        """Wrapper for pain point analysis."""
        try:
            # Parse input - expected format: "prospect_name|prospect_title|prospect_company|prospect_industry|company_size|recent_news|linkedin_summary|skills"
            parts = [part.strip() for part in query.split('|')]
            if len(parts) >= 8:
                prospect_name, prospect_title, prospect_company, prospect_industry, company_size, recent_news, linkedin_summary, skills = parts[:8]
            else:
                # Fallback: treat as general prospect information
                prospect_name = prospect_title = prospect_company = prospect_industry = company_size = recent_news = linkedin_summary = skills = query

            # Use LLM to analyze pain points
            prompt = PersonalizationPrompts.get_pain_point_analysis_prompt()
            formatted_prompt = prompt.format(
                prospect_name=prospect_name,
                prospect_title=prospect_title,
                prospect_company=prospect_company,
                prospect_industry=prospect_industry,
                company_size=company_size,
                recent_news=recent_news,
                linkedin_summary=linkedin_summary,
                skills=skills
            )

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing pain points: {str(e)}")
            return f"Error analyzing pain points: {str(e)}"

    def _analyze_value_alignment_wrapper(self, query: str) -> str:
        """Wrapper for value alignment analysis."""
        try:
            # Parse input - expected format: "prospect_profile||solution_name||key_benefits||target_problems||unique_differentiators"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 5:
                prospect_profile, solution_name, key_benefits, target_problems, unique_differentiators = parts[:5]
            else:
                # Fallback values
                prospect_profile = query
                solution_name = "Our Solution"
                key_benefits = "Increased efficiency, cost savings, improved performance"
                target_problems = "Operational inefficiencies, high costs, manual processes"
                unique_differentiators = "Proprietary technology, proven results, expert support"

            # Use LLM to analyze value alignment
            prompt = PersonalizationPrompts.get_value_alignment_prompt()
            formatted_prompt = prompt.format(
                prospect_profile=prospect_profile,
                solution_name=solution_name,
                key_benefits=key_benefits,
                target_problems=target_problems,
                unique_differentiators=unique_differentiators
            )

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing value alignment: {str(e)}")
            return f"Error analyzing value alignment: {str(e)}"

    def create_prospect_profile(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a detailed prospect profile from research data.

        Args:
            research_data: Dictionary containing research findings from ResearchAgent

        Returns:
            Dictionary containing the personalized prospect profile
        """
        logger.info("Creating prospect profile from research data")

        try:
            # Prepare research data for the agent
            research_summary = self._prepare_research_summary(research_data)

            # Build prospect profile
            profile_result = self._build_prospect_profile_wrapper(research_summary)

            # Extract key information for structured profile
            prospect_profile = {
                "raw_research": research_data,
                "research_summary": research_summary,
                "detailed_profile": profile_result,
                "personalization_hooks": self._extract_personalization_hooks(profile_result),
                "likely_pain_points": self._extract_pain_points(research_data),
                "communication_style": self._determine_communication_style(research_data),
                "timestamp": self._get_timestamp()
            }

            logger.info("Prospect profile created successfully")
            return prospect_profile

        except Exception as e:
            logger.error(f"Error creating prospect profile: {str(e)}")
            return {
                "error": str(e),
                "raw_research": research_data,
                "timestamp": self._get_timestamp()
            }

    def _prepare_research_summary(self, research_data: Dict[str, Any]) -> str:
        """Prepare a summary of research data for processing."""
        summary_parts = []

        if "company_research" in research_data:
            summary_parts.append(f"Company Research: {research_data['company_research']}")

        if "linkedin_profile" in research_data:
            profile = research_data["linkedin_profile"]
            if isinstance(profile, dict):
                summary_parts.append(
                    f"LinkedIn Profile: {profile.get('full_name', 'Unknown')} - "
                    f"{profile.get('title', 'Unknown Title')} at {profile.get('company', 'Unknown Company')}"
                )
            else:
                summary_parts.append(f"LinkedIn Profile: {profile}")

        if "industry_research" in research_data:
            summary_parts.append(f"Industry Research: {research_data['industry_research']}")

        if "synthesized_research" in research_data:
            summary_parts.append(f"Key Insights: {research_data['synthesized_research']}")

        return "\n\n".join(summary_parts) if summary_parts else "Limited research data available"

    def _extract_personalization_hooks(self, profile_text: str) -> list:
        """Extract specific personalization hooks from profile text."""
        # In a real implementation, this would use NLP to extract specific details
        # For now, return some generic hooks based on common patterns
        hooks = [
            "Reference to recent company news or developments",
            "Mention of specific role responsibilities",
            "Reference to educational background",
            "Mention of specific skills or expertise",
            "Reference to professional activity or posts",
            "Congratulations on recent achievements",
            "Reference to mutual connections or groups",
            "Reference to location or local events"
        ]
        # Return a subset as examples
        return hooks[:3]

    def _extract_pain_points(self, research_data: Dict[str, Any]) -> list:
        """Extract likely pain points from research data."""
        # Common pain points by role/industry - in reality would come from LLM analysis
        common_pain_points = [
            "Scaling operations efficiently",
            "Reducing customer acquisition costs",
            "Improving employee retention",
            "Modernizing legacy systems",
            "Competing with new entrants",
            "Managing remote work productivity",
            "Adapting to regulatory changes",
            "Improving data-driven decision making"
        ]
        return common_pain_points[:4]  # Return top 4

    def _determine_communication_style(self, research_data: Dict[str, Any]) -> str:
        """Determine likely communication style based on research."""
        # Simple heuristic - in reality would analyze LinkedIn posts, summary, etc.
        styles = ["Direct and data-driven", "Collaborative and relationship-focused",
                  "Innovative and forward-thinking", "Practical and results-oriented"]
        return styles[0]  # Default - would be determined by analysis

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_profile_summary(self, profile_data: Dict[str, Any]) -> str:
        """Get a formatted summary of the prospect profile."""
        if "error" in profile_data:
            return f"Profile Error: {profile_data['error']}"

        summary_parts = []

        if "detailed_profile" in profile_data:
            summary_parts.append(f"Detailed Profile:\n{profile_data['detailed_profile']}")

        if "personalization_hooks" in profile_data:
            hooks = ", ".join(profile_data["personalization_hooks"])
            summary_parts.append(f"Personalization Hooks: {hooks}")

        if "likely_pain_points" in profile_data:
            pain_points = ", ".join(profile_data["likely_pain_points"])
            summary_parts.append(f"Likely Pain Points: {pain_points}")

        return "\n\n".join(summary_parts) if summary_parts else "No profile data available"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = PersonalizationAgent()

    # Test with sample research data
    sample_research = {
        "company_name": "Acme Corp",
        "company_research": {
            "name": "Acme Corp",
            "industry": "technology",
            "recent_news": ["recently launched a new AI-powered product", "secured Series B funding round"],
            "key_challenges": ["scaling operations efficiently", "reducing customer acquisition costs"]
        },
        "linkedin_profile": {
            "full_name": "John Doe",
            "title": "VP of Engineering",
            "company": "Acme Corp",
            "summary": "Experienced engineering leader with focus on scaling teams and implementing new technologies",
            "skills": ["Leadership", "Software Architecture", "Team Management", "AWS"]
        }
    }

    profile = agent.create_prospect_profile(sample_research)
    print("Prospect Profile:")
    print(agent.get_profile_summary(profile))