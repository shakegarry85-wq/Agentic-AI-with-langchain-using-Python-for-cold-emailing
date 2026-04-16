"""
Prompt templates for the Email Writer Agent.
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any

class EmailWriterPrompts:
    """Collection of prompt templates for email writing tasks."""

    @staticmethod
    def get_email_generation_prompt() -> PromptTemplate:
        """Prompt for generating personalized cold emails."""
        template = """
        You are an expert cold email copywriter specializing in highly personalized outreach that gets responses.

        Prospect Profile:
        {prospect_profile}

        Personalization Insights:
        {personalization_insights}

        Value Proposition:
        {value_proposition}

        Instructions:
        Write a highly personalized cold email using one of these proven frameworks:
        1. AIDA (Attention, Interest, Desire, Action)
        2. PAS (Problem, Agitate, Solution)
        3. Before-After-Bridge (BAB)

        Requirements:
        - Subject line: Compelling, personalized, under 50 characters
        - Opening: Reference something specific from their profile/research
        - Body: Focus on their pain points and how we solve them
        - Social proof: Include brief, relevant credibility builder
        - Call-to-Action: Clear, low-pressure, specific next step
        - Length: 80-150 words total (excluding subject line)
        - Tone: Professional yet conversational, respectful of their time
        - Personalization: Use at least 3 specific details from their profile
        - Avoid: Generic templates, spammy language, excessive flattery

        Framework Selection Guidance:
        - Use AIDA for prospects who may not know they have a problem
        - Use PAS for prospects who are aware of their pain points
        - Use BAB when you can clearly show transformation

        Output Format:
        SUBJECT: [subject line here]

        EMAIL BODY:
        [email body here]

        PERSONALIZATION NOTES:
        [brief explanation of what was personalized and why]
        """

        return PromptTemplate(
            input_variables=["prospect_profile", "personalization_insights", "value_proposition"],
            template=template
        )

    @staticmethod
    def get_subject_line_optimization_prompt() -> PromptTemplate:
        """Prompt for optimizing subject lines."""
        template = """
        You are a subject line optimization expert for cold email outreach.

        Current Subject Line: {current_subject}
        Prospect Profile: {prospect_profile}
        Email Context: {email_context}

        Generate 5 subject line variations that:
        1. Are highly personalized (include specific details from prospect profile)
        2. Create curiosity or urgency without being spammy
        3. Are under 50 characters for full mobile visibility
        4. Avoid spam trigger words (free, guarantee, winner, etc.)
        5. Match the tone and content of the email body
        6. Would stand out in a crowded inbox

        For each subject line, provide:
        - The subject line text
        - Personalization elements used
        - Psychological principle leveraged (curiosity, urgency, relevance, etc.)
        - Estimated open rate impact

        Subject Line Variations:
        """

        return PromptTemplate(
            input_variables=["current_subject", "prospect_profile", "email_context"],
            template=template
        )

    @staticmethod
    def get_framework_selection_prompt() -> PromptTemplate:
        """Prompt for selecting the best email framework."""
        template = """
        You are an email strategy specialist tasked with selecting the optimal framework for a cold email.

        Prospect Information:
        {prospect_information}

        Pain Points Identified:
        {pain_points}

        Prospect Awareness Level: {awareness_level}
        (Unaware = doesn't know they have problem, Problem Aware = knows problem exists, Solution Aware = looking for solutions)

        Based on the prospect's awareness level and pain points, recommend:
        1. Which framework to use: AIDA, PAS, or BAB
        2. Why this framework is optimal for this prospect
        3. How to adapt the framework to their specific situation
        4. Key elements to emphasize in each section
        5. Potential pitfalls to avoid with this framework

        Framework Recommendation:
        """

        return PromptTemplate(
            input_variables=["prospect_information", "pain_points", "awareness_level"],
            template=template
        )


# Example usage
if __name__ == "__main__":
    # Test prompt creation
    email_prompt = EmailWriterPrompts.get_email_generation_prompt()
    print("Email Generation Prompt:")
    print(email_prompt.template)
    print("\n" + "="*50 + "\n")

    subject_prompt = EmailWriterPrompts.get_subject_line_optimization_prompt()
    print("Subject Line Optimization Prompt:")
    print(subject_prompt.template)