"""
Email Writer Agent for generating personalized cold emails.
Uses LangChain to create highly personalized email content.
"""

import logging
from typing import Dict, Any, Optional
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from prompts.email_writer_prompt import EmailWriterPrompts

logger = logging.getLogger(__name__)

class EmailWriterAgent:
    """Agent responsible for generating personalized cold emails."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)

        # Initialize tools for the agent
        self.tools = [
            Tool(
                name="EmailGenerator",
                func=self._generate_email_wrapper,
                description="Generate a personalized cold email using frameworks like AIDA or PAS. Input should contain prospect profile, personalization insights, and value proposition."
            ),
            Tool(
                name="SubjectLineOptimizer",
                func=self._optimize_subject_line_wrapper,
                description="Optimize subject lines for higher open rates. Input should contain current subject, prospect profile, and email context."
            ),
            Tool(
                name="FrameworkSelector",
                func=self._select_framework_wrapper,
                description="Select the optimal email framework (AIDA, PAS, BAB) based on prospect awareness level. Input should contain prospect information and pain points."
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

        logger.info("Email Writer Agent initialized")

    def _generate_email_wrapper(self, query: str) -> str:
        """Wrapper for email generation."""
        try:
            # Parse input - expected format: "prospect_profile||personalization_insights||value_proposition"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 3:
                prospect_profile, personalization_insights, value_proposition = parts[:3]
            else:
                # Fallback values
                prospect_profile = query
                personalization_insights = "Professional in technology sector with leadership role"
                value_proposition = "Our solution improves efficiency and reduces costs"

            # Use LLM to generate email
            prompt = EmailWriterPrompts.get_email_generation_prompt()
            formatted_prompt = prompt.format(
                prospect_profile=prospect_profile,
                personalization_insights=personalization_insights,
                value_proposition=value_proposition
            )

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            return f"Error generating email: {str(e)}"

    def _optimize_subject_line_wrapper(self, query: str) -> str:
        """Wrapper for subject line optimization."""
        try:
            # Parse input - expected format: "current_subject||prospect_profile||email_context"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 3:
                current_subject, prospect_profile, email_context = parts[:3]
            else:
                # Fallback values
                current_subject = query
                prospect_profile = "Technology professional"
                email_context = "Cold email outreach"

            # Use LLM to optimize subject line
            prompt = EmailWriterPrompts.get_subject_line_optimization_prompt()
            formatted_prompt = prompt.format(
                current_subject=current_subject,
                prospect_profile=prospect_profile,
                email_context=email_context
            )

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error optimizing subject line: {str(e)}")
            return f"Error optimizing subject line: {str(e)}"

    def _select_framework_wrapper(self, query: str) -> str:
        """Wrapper for framework selection."""
        try:
            # Parse input - expected format: "prospect_information||pain_points||awareness_level"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 3:
                prospect_information, pain_points, awareness_level = parts[:3]
            else:
                # Fallback values
                prospect_information = query
                pain_points = "Operational inefficiencies"
                awareness_level = "Problem Aware"

            # Use LLM to select framework
            prompt = EmailWriterPrompts.get_framework_selection_prompt()
            formatted_prompt = prompt.format(
                prospect_information=prospect_information,
                pain_points=pain_points,
                awareness_level=awareness_level
            )

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error selecting framework: {str(e)}")
            return f"Error selecting framework: {str(e)}"

    def generate_email(self,
                      prospect_profile: Dict[str, Any],
                      personalization_insights: Dict[str, Any],
                      value_proposition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a personalized cold email.

        Args:
            prospect_profile: Output from PersonalizationAgent
            personalization_insights: Additional personalization data
            value_proposition: Details about our solution and benefits

        Returns:
            Dictionary containing the generated email and metadata
        """
        logger.info("Generating personalized cold email")

        try:
            # Prepare inputs for the agent
            profile_text = self._format_dict_for_prompt(prospect_profile)
            insights_text = self._format_dict_for_prompt(personalization_insights)
            value_text = self._format_dict_for_prompt(value_proposition)

            # Combine inputs
            input_text = f"{profile_text}||{insights_text}||{value_text}"

            # Generate email
            email_result = self._generate_email_wrapper(input_text)

            # Parse the result to extract subject and body
            parsed_email = self._parse_generated_email(email_result)

            # Add metadata
            result = {
                "generated_email": parsed_email,
                "raw_generation": email_result,
                "prospect_profile_used": prospect_profile,
                "personalization_insights_used": personalization_insights,
                "value_proposition_used": value_proposition,
                "generation_timestamp": self._get_timestamp()
            }

            logger.info("Email generated successfully")
            return result

        except Exception as e:
            logger.error(f"Error generating email: {str(e)}")
            return {
                "error": str(e),
                "generation_timestamp": self._get_timestamp()
            }

    def _format_dict_for_prompt(self, data: Dict[str, Any]) -> str:
        """Format a dictionary as text for prompting."""
        if not isinstance(data, dict):
            return str(data)

        formatted_parts = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                formatted_parts.append(f"{key}: {value}")
            else:
                formatted_parts.append(f"{key}: {value}")
        return "\n".join(formatted_parts)

    def _parse_generated_email(self, email_text: str) -> Dict[str, Any]:
        """Parse the generated email to extract subject and body."""
        result = {
            "subject": "",
            "body": "",
            "personalization_notes": "",
            "framework_used": "Unknown"
        }

        try:
            lines = email_text.split('\n')
            subject_found = False
            body_found = False
            notes_found = False
            current_section = None

            for line in lines:
                line_stripped = line.strip()

                if line_stripped.startswith("SUBJECT:"):
                    result["subject"] = line_stripped[8:].strip()
                    subject_found = True
                    current_section = "subject"
                elif line_stripped.startswith("EMAIL BODY:"):
                    current_section = "body"
                    body_found = True
                elif line_stripped.startswith("PERSONALIZATION NOTES:"):
                    current_section = "notes"
                    notes_found = True
                elif line_stripped and not line_stripped.startswith("["):
                    # Content line
                    if current_section == "subject" and not result["subject"]:
                        # Handle case where subject is on next line
                        result["subject"] = line_stripped
                    elif current_section == "body":
                        if result["body"]:
                            result["body"] += "\n" + line_stripped
                        else:
                            result["body"] = line_stripped
                    elif current_section == "notes":
                        if result["personalization_notes"]:
                            result["personalization_notes"] += "\n" + line_stripped
                        else:
                            result["personalization_notes"] = line_stripped

            # If we didn't find structured format, treat entire text as body
            if not result["subject"] and not result["body"]:
                result["body"] = email_text.strip()
                # Try to extract a subject from first line
                lines = result["body"].split('\n')
                if lines and len(lines[0]) < 100:  # Reasonable subject length
                    result["subject"] = lines[0]
                    result["body"] = '\n'.join(lines[1:]).strip()

        except Exception as e:
            logger.error(f"Error parsing generated email: {str(e)}")
            result["body"] = email_text  # Fallback to raw text

        return result

    def optimize_subject_line(self,
                             current_subject: str,
                             prospect_profile: Dict[str, Any],
                             email_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Optimize subject line for higher open rates.

        Args:
            current_subject: Current subject line
            prospect_profile: Prospect information
            email_context: Additional context about the email

        Returns:
            Dictionary containing optimized subject lines and analysis
        """
        logger.info("Optimizing subject line")

        try:
            profile_text = self._format_dict_for_prompt(prospect_profile)
            context_text = self._format_dict_for_prompt(email_context or {})

            input_text = f"{current_subject}||{profile_text}||{context_text}"
            optimization_result = self._optimize_subject_line_wrapper(input_text)

            return {
                "optimization_result": optimization_result,
                "current_subject": current_subject,
                "prospect_profile_used": prospect_profile,
                "optimization_timestamp": self._get_timestamp()
            }

        except Exception as e:
            logger.error(f"Error optimizing subject line: {str(e)}")
            return {
                "error": str(e),
                "optimization_timestamp": self._get_timestamp()
            }

    def select_framework(self,
                        prospect_information: Dict[str, Any],
                        pain_points: Dict[str, Any],
                        awareness_level: str) -> Dict[str, Any]:
        """
        Select the optimal email framework.

        Args:
            prospect_information: Details about the prospect
            pain_points: Identified pain points
            awareness_level: Prospect's awareness level (Unaware, Problem Aware, Solution Aware)

        Returns:
            Dictionary containing framework recommendation and reasoning
        """
        logger.info("Selecting email framework")

        try:
            prospect_text = self._format_dict_for_prompt(prospect_information)
            pain_text = self._format_dict_for_prompt(pain_points)

            input_text = f"{prospect_text}||{pain_text}||{awareness_level}"
            framework_result = self._select_framework_wrapper(input_text)

            return {
                "framework_recommendation": framework_result,
                "prospect_information_used": prospect_information,
                "pain_points_used": pain_points,
                "awareness_level": awareness_level,
                "selection_timestamp": self._get_timestamp()
            }

        except Exception as e:
            logger.error(f"Error selecting framework: {str(e)}")
            return {
                "error": str(e),
                "selection_timestamp": self._get_timestamp()
            }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_email_summary(self, email_data: Dict[str, Any]) -> str:
        """Get a formatted summary of the generated email."""
        if "error" in email_data:
            return f"Email Generation Error: {email_data['error']}"

        summary_parts = []

        if "generated_email" in email_data:
            email = email_data["generated_email"]
            summary_parts.append(f"Subject: {email.get('subject', 'No subject')}")
            summary_parts.append(f"Body:\n{email.get('body', 'No body')}")
            if email.get('personalization_notes'):
                summary_parts.append(f"Personalization Notes:\n{email['personalization_notes']}")

        return "\n\n".join(summary_parts) if summary_parts else "No email data available"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = EmailWriterAgent()

    # Test with sample data
    sample_profile = {
        "full_name": "John Doe",
        "title": "VP of Engineering",
        "company": "Acme Corp",
        "industry": "technology",
        "recent_news": ["launched AI-powered product", "secured Series B funding"],
        "pain_points": ["scaling operations", "reducing costs"]
    }

    sample_insights = {
        "personalization_hooks": ["reference to recent product launch", "mention of Series B funding"],
        "communication_style": "data-driven and results-focused"
    }

    sample_value = {
        "solution_name": "TechOptimize Pro",
        "key_benefits": ["30% faster deployment", "50% reduction in infrastructure costs"],
        "target_problems": ["scaling challenges", "high operational costs"],
        "unique_differentiators": ["AI-powered optimization", "24/7 expert support"]
    }

    email_result = agent.generate_email(sample_profile, sample_insights, sample_value)
    print("Generated Email:")
    print(agent.get_email_summary(email_result))