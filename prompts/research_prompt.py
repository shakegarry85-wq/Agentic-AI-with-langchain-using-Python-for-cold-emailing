"""
Prompt templates for the Research Agent.
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any

class ResearchPrompts:
    """Collection of prompt templates for research tasks."""

    @staticmethod
    def get_company_research_prompt() -> PromptTemplate:
        """Prompt for researching company information."""
        template = """
        You are a research specialist tasked with gathering information about a company for cold email outreach.

        Company Name: {company_name}
        Industry: {industry}
        LinkedIn URL: {linkedin_url}

        Based on the available information, provide:
        1. Recent news or developments about the company (last 3-6 months)
        2. Key challenges or pain points the company might be facing
        3. Company size, growth stage, and market position
        4. Recent initiatives, product launches, or strategic changes
        5. Any notable achievements or awards

        Focus on information that would be relevant for personalizing a cold email.
        Present your findings in a clear, structured format suitable for the personalization agent.

        Research Findings:
        """

        return PromptTemplate(
            input_variables=["company_name", "industry", "linkedin_url"],
            template=template
        )

    @staticmethod
    def get_linkedin_research_prompt() -> PromptTemplate:
        """Prompt for researching LinkedIn profile information."""
        template = """
        You are a research specialist tasked with gathering information from a LinkedIn profile for cold email outreach.

        Profile Information:
        - Name: {full_name}
        - Title: {title}
        - Company: {company}
        - Industry: {industry}
        - Location: {location}
        - Experience Years: {experience_years}
        - Education: {education}
        - Skills: {skills}
        - Summary: {summary}

        Based on this LinkedIn profile, provide:
        1. Professional background and expertise areas
        2. Current role responsibilities and likely priorities
        3. Potential pain points or challenges in their role
        4. Professional interests based on activity and summary
        5. How they might benefit from solutions in your industry

        Focus on insights that would help personalize an outreach message.
        Present your findings in a clear, structured format.

        LinkedIn Research Findings:
        """

        return PromptTemplate(
            input_variables=[
                "full_name", "title", "company", "industry", "location",
                "experience_years", "education", "skills", "summary"
            ],
            template=template
        )

    @staticmethod
    def get_industry_trends_prompt() -> PromptTemplate:
        """Prompt for researching industry trends."""
        template = """
        You are researching industry trends for {industry} to better understand the business context.

        Provide insights on:
        1. Current trends and developments in the {industry} industry
        2. Common challenges companies in this industry face
        3. Emerging technologies or methodologies gaining adoption
        4. Regulatory or market changes affecting the industry
        5. Best practices and successful strategies in this space

        This information will be used to tailor cold email outreach to prospects in this industry.

        Industry Trends Analysis:
        """

        return PromptTemplate(
            input_variables=["industry"],
            template=template
        )


# Example usage
if __name__ == "__main__":
    # Test prompt creation
    company_prompt = ResearchPrompts.get_company_research_prompt()
    print("Company Research Prompt:")
    print(company_prompt.template)
    print("\n" + "="*50 + "\n")

    linkedin_prompt = ResearchPrompts.get_linkedin_research_prompt()
    print("LinkedIn Research Prompt:")
    print(linkedin_prompt.template)