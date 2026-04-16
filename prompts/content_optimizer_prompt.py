"""
Prompt templates for the Content Optimizer Agent.
"""

from langchain.prompts import PromptTemplate
from typing import Dict, Any

class ContentOptimizerPrompts:
    """Collection of prompt templates for content optimization tasks."""

    @staticmethod
    def get_content_optimization_prompt() -> PromptTemplate:
        """Prompt for optimizing email content."""
        template = """
        You are a content optimization specialist for cold email outreach.
        Your goal is to improve email effectiveness while maintaining personalization and professionalism.

        Email Content:
        Subject: {subject}
        Body: {body}

        Optimization Goals:
        1. Improve subject line open rate potential
        2. Enhance readability and scannability
        3. Strengthen call-to-action clarity
        4. Reduce spam score
        5. Maintain or improve personalization level
        6. Ensure professional tone

        Please provide:
        1. Optimized subject line (with explanation of changes)
        2. Optimized email body (with explanation of changes)
        3. Readability score improvement suggestions
        4. Spam score reduction recommendations
        5. CTA optimization suggestions
        6. Overall effectiveness score (1-10) before and after optimization

        Optimization Results:
        """

        return PromptTemplate(
            input_variables=["subject", "body"],
            template=template
        )

    @staticmethod
    def get_readability_analysis_prompt() -> PromptTemplate:
        """Prompt for analyzing and improving readability."""
        template = """
        You are a readability expert analyzing cold email content.

        Email Body: {body}

        Analyze the email for:
        1. Reading level (aim for 8th grade or lower for broad accessibility)
        2. Sentence length and complexity
        3. Paragraph structure and scannability
        4. Use of jargon or complex terms
        5. Flow and logical progression

        Provide:
        1. Current readability score (Flesch-Kincaid Grade Level)
        2. Specific suggestions to improve readability
        3. Rewritten version with improved readability
        4. Explanation of changes made

        Readability Analysis:
        """

        return PromptTemplate(
            input_variables=["body"],
            template=template
        )

    @staticmethod
    def get_cta_optimization_prompt() -> PromptTemplate:
        """Prompt for optimizing call-to-action."""
        template = """
        You are a conversion optimization specialist analyzing cold email call-to-actions.

        Email Body: {body}
        Current CTA: {current_cta}
        Prospect Profile: {prospect_profile}

        Analyze the CTA for:
        1. Clarity and specificity
        2. Low pressure and ease of response
        3. Value proposition alignment
        4. Visual prominence (in text format)
        5. Psychological effectiveness

        Provide:
        1. Evaluation of current CTA effectiveness (1-10)
        2. 3-5 alternative CTA options with explanations
        3. Recommended CTA and why it's optimal
        4. Placement suggestions within the email

        CTA Optimization Results:
        """

        return PromptTemplate(
            input_variables=["body", "current_cta", "prospect_profile"],
            template=template
        )


# Example usage
if __name__ == "__main__":
    # Test prompt creation
    opt_prompt = ContentOptimizerPrompts.get_content_optimization_prompt()
    print("Content Optimization Prompt:")
    print(opt_prompt.template)
    print("\n" + "="*50 + "\n")

    readability_prompt = ContentOptimizerPrompts.get_readability_analysis_prompt()
    print("Readability Analysis Prompt:")
    print(readability_prompt.template)