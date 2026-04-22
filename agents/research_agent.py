"""
Research Agent for gathering company and prospect information.
Uses LangChain tools and LLMs to research prospects.
"""

import logging
from typing import Dict, Any, Optional
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool

from tools.research_tool import ResearchTool
from tools.linkedin_tool import LinkedInTool
from prompts.research_prompt import ResearchPrompts

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Agent responsible for researching companies and prospects."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.1):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.research_tool = ResearchTool()
        self.linkedin_tool = LinkedInTool()

        # Initialize tools for the agent
        self.tools = [
            Tool(
                name="CompanyResearch",
                func=self._research_company_wrapper,
                description="Research a company for recent news, challenges, and background information. Input should be company name and optionally industry."
            ),
            Tool(
                name="LinkedInResearch",
                func=self._research_linkedin_wrapper,
                description="Research a LinkedIn profile for professional background, skills, and activity. Input should be LinkedIn URL."
            ),
            Tool(
                name="IndustryResearch",
                func=self._research_industry_wrapper,
                description="Research industry trends and common challenges. Input should be industry name."
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

        logger.info("Research Agent initialized")

    def _research_company_wrapper(self, query: str) -> str:
        """Wrapper for company research tool."""
        try:
            # Parse input - could be "company_name" or "company_name, industry"
            parts = [part.strip() for part in query.split(',')]
            company_name = parts[0]
            industry = parts[1] if len(parts) > 1 else None

            result = self.research_tool.research_company(company_name, industry)
            return f"Company Research Results:\n{result}"
        except Exception as e:
            logger.error(f"Error in company research: {str(e)}")
            return f"Error researching company: {str(e)}"

    def _research_linkedin_wrapper(self, query: str) -> str:
        """Wrapper for LinkedIn research tool."""
        try:
            linkedin_url = query.strip()
            result = self.linkedin_tool.extract_profile_info(linkedin_url)
            return f"LinkedIn Profile Results:\n{result}"
        except Exception as e:
            logger.error(f"Error in LinkedIn research: {str(e)}")
            return f"Error researching LinkedIn profile: {str(e)}"

    def _research_industry_wrapper(self, query: str) -> str:
        """Wrapper for industry research tool."""
        try:
            industry = query.strip()
            # For now, return generic industry insights
            # In a real implementation, this could use web search or industry databases
            insights = {
                "industry": industry,
                "trends": [
                    f"Increasing adoption of AI and automation in {industry}",
                    f"Growing focus on customer experience and personalization",
                    f"Remote work and distributed teams becoming standard",
                    f"Increased regulatory compliance requirements",
                    f"Consolidation through mergers and acquisitions"
                ],
                "challenges": [
                    f"Talent acquisition and retention in {industry}",
                    f"Keeping up with rapid technological changes",
                    f"Managing cost pressures while innovating",
                    f"Data privacy and security concerns",
                    f"Adapting to changing customer expectations"
                ],
                "opportunities": [
                    f"Digital transformation initiatives",
                    f"Expansion into new markets or segments",
                    f"Strategic partnerships and alliances",
                    f"Product/service innovation",
                    f"Operational efficiency improvements"
                ]
            }
            return f"Industry Research Results:\n{insights}"
        except Exception as e:
            logger.error(f"Error in industry research: {str(e)}")
            return f"Error researching industry: {str(e)}"

    def research_prospect(self,
                         company_name: str,
                         linkedin_url: Optional[str] = None,
                         industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Research a prospect using company and/or LinkedIn information.

        Args:
            company_name: Name of the prospect's company
            linkedin_url: Optional LinkedIn profile URL
            industry: Optional industry classification

        Returns:
            Dictionary containing comprehensive research data
        """
        logger.info(f"Starting research for prospect at {company_name}")

        research_data = {
            "company_name": company_name,
            "linkedin_url": linkedin_url,
            "industry": industry,
            "timestamp": None  # Will be set after research
        }

        try:
            # Research company
            if company_name:
                company_result = self.research_tool.research_company(company_name, industry)
                research_data["company_research"] = company_result
                logger.info("Company research completed")

            # Research LinkedIn profile if provided
            if linkedin_url:
                linkedin_result = self.linkedin_tool.extract_profile_info(linkedin_url)
                research_data["linkedin_profile"] = linkedin_result
                logger.info("LinkedIn research completed")

            # Research industry if not provided or to get more details
            if industry or company_name:
                # Infer industry if not provided
                if not industry and company_name:
                    industry = self.research_tool._infer_industry(company_name)
                industry_result = self._research_industry_wrapper(industry or "technology")
                research_data["industry_research"] = industry_result
                logger.info("Industry research completed")

            # Use LLM to synthesize and enhance the research
            synthesized_research = self._synthesize_research_with_llm(research_data)
            research_data["synthesized_research"] = synthesized_research
            research_data["timestamp"] = self._get_timestamp()

            logger.info(f"Research completed for {company_name}")
            return research_data

        except Exception as e:
            logger.error(f"Error during prospect research: {str(e)}")
            research_data["error"] = str(e)
            return research_data

    def _synthesize_research_with_llm(self, research_data: Dict[str, Any]) -> str:
        """Use LLM to synthesize research data into key insights."""
        try:
            # Prepare context for LLM
            context_parts = []

            if "company_research" in research_data:
                context_parts.append(f"Company Research:\n{research_data['company_research']}")

            if "linkedin_profile" in research_data:
                context_parts.append(f"LinkedIn Profile:\n{research_data['linkedin_profile']}")

            if "industry_research" in research_data:
                context_parts.append(f"Industry Research:\n{research_data['industry_research']}")

            context = "\n\n".join(context_parts)

            # Create synthesis prompt
            synthesis_prompt = f"""
            You are a research analyst tasked with synthesizing information about a prospect for cold email outreach.

            Based on the following research data, provide:
            1. Key company insights (recent developments, challenges, opportunities)
            2. Key professional insights about the prospect (role, background, likely priorities)
            3. Industry context and trends that are relevant
            4. Specific personalization opportunities for outreach
            5. Likely pain points based on role, company, and industry

            Research Data:
            {context}

            Synthesized Insights:
            """

            # Get LLM response
            messages = [SystemMessage(content=synthesis_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error synthesizing research with LLM: {str(e)}")
            return f"Research data available but synthesis failed: {str(e)}"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_research_summary(self, research_data: Dict[str, Any]) -> str:
        """Get a formatted summary of research data."""
        if "error" in research_data:
            return f"Research Error: {research_data['error']}"

        summary_parts = []

        if "synthesized_research" in research_data:
            summary_parts.append(f"Key Insights:\n{research_data['synthesized_research']}")

        if "company_research" in research_data:
            summary_parts.append(f"Company Details:\n{research_data['company_research']}")

        if "linkedin_profile" in research_data:
            profile = research_data["linkedin_profile"]
            if isinstance(profile, dict):
                summary_parts.append(f"LinkedIn Profile: {profile.get('full_name', 'Unknown')} - {profile.get('title', 'Unknown Title')} at {profile.get('company', 'Unknown Company')}")
            else:
                summary_parts.append(f"LinkedIn Profile:\n{profile}")

        return "\n\n".join(summary_parts) if summary_parts else "No research data available"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = ResearchAgent()

    # Test research
    result = agent.research_prospect(
        company_name="Acme Corp",
        linkedin_url="https://linkedin.com/in/johndoe",
        industry="technology"
    )

    print("Research Results:")
    print(agent.get_research_summary(result))