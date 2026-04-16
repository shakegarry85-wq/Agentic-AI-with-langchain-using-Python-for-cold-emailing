"""
Prompt templates for the Personalization Agent.
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any

class PersonalizationPrompts:
    """Collection of prompt templates for personalization tasks."""

    @staticmethod
    def get_prospect_profile_prompt() -> PromptTemplate:
        """Prompt for building a prospect profile."""
        template = """
        You are a personalization specialist tasked with creating a detailed prospect profile for cold email outreach.

        Research Data:
        {research_data}

        Based on the research data provided, create a comprehensive prospect profile that includes:
        1. Professional Background: Role, responsibilities, expertise level
        2. Company Context: Industry position, company size, recent developments
        3. Likely Pain Points: Based on role, industry, and company situation
        4. Professional Interests: From LinkedIn activity, skills, and summary
        5. Communication Preferences: How this person likely prefers to be contacted
        6. Value Proposition Alignment: How our solution addresses their specific needs
        7. Personalization Hooks: Specific details we can reference in outreach

        Present this as a structured profile that the email writer agent can use to generate highly personalized content.

        Prospect Profile:
        """

        return PromptTemplate(
            input_variables=["research_data"],
            template=template
        )

    @staticmethod
    def get_pain_point_analysis_prompt() -> PromptTemplate:
        """Prompt for analyzing prospect pain points."""
        template = """
        You are analyzing the likely pain points and challenges for a prospect based on their role, company, and industry.

        Prospect Information:
        - Name: {prospect_name}
        - Title: {prospect_title}
        - Company: {prospect_company}
        - Industry: {prospect_industry}
        - Company Size: {company_size}
        - Recent News: {recent_news}
        - LinkedIn Summary: {linkedin_summary}
        - Skills: {skills}

        Based on this information, identify:
        1. Top 3-5 likely business challenges this person faces
        2. How these challenges impact their daily responsibilities
        3. What solutions would be valuable to them?
        4. How their career progression depends
        5. Quantify the costs of where these challenges include to time, money, reputation risk?
        Format your analysis around business impact severity.

        Pain Point Analysis:
        Pain Point Analysis:
        """
        Pain: format This template but isn't right due to cutoff. Let me rewrite it properly. Since this got cut off the prompt properly.

        """
        return Prompt variables=["prospect_name", "prospect_title"<d="1"nCompany":<<{teturn(
    promptinput_variables=["role", the "industry": company", to"{prospect_industry}".description",: "recent_news",
    template=template
}
    @staticmethod
    def get_value_alignment_prompt() -> PromptTemplate:
        """Prompt for aligning value proposition with prospect needs."""
        template = """
        You are aligning our solution's value proposition with the specific needs and challenges of a prospect.

        Prospect Profile:
        {prospect_profile}

        Our Solution:
        - Solution Name: {solution_name}
        - Key Benefits: {key_benefits"
        - Target Problems: {target_problems}
        - Unique Differentiators: {unique_differentiators}

        Based on the prospect profile and our solution details, provide:
        1. Specific ways our solution addresses the prospect's likely pain points
        2. Quantifiable benefits that would resonate with this prospect
        3. How our solution compares to alternatives they might be considering
        4. ROI considerations that would matter to someone in their role
        5. Talking points for initial outreach conversation

        Value Alignment Analysis:
        """

        return PromptTemplate(
            input_variables=["prospect_profile", "solution_name", "key_benefits", "target_problems", "unique_differentiators"],
            template=template
        )


# Example usage
if __name__ == "__main__":
    # Test prompt creation
    profile_prompt = PersonalizationPrompts.get_prospect_profile_prompt()
    print("Prospect Profile Prompt:")
    print(profile_prompt.template)
    print("\n" + "="*50 + "\n")

    pain_prompt = PersonalizationPrompts.get_pain_point_analysis_prompt()
    print("Pain Point Analysis Prompt:")
    print(pain_prompt.template)