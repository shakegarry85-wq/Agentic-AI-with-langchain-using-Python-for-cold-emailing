"""
Content Optimizer Agent for improving email content.
Uses LangChain to optimize subject lines, readability, CTA, and spam score.
"""

import logging
from typing import Dict, Any, Optional
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool

from prompts.content_optimizer_prompt import ContentOptimizerPrompts
from tools.spam_checker_tool import SpamCheckerTool

logger = logging.getLogger(__name__)

class ContentOptimizerAgent:
    """Agent responsible for optimizing email content."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.3):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.spam_checker = SpamCheckerTool()

        # Initialize tools for the agent
        self.tools = [
            Tool(
                name="ContentOptimizer",
                func=self._optimize_content_wrapper,
                description="Optimize email content for better performance. Input should contain subject and body."
            ),
            Tool(
                name="ReadabilityAnalyzer",
                func=self._analyze_readability_wrapper,
                description="Analyze and improve email readability. Input should be email body."
            ),
            Tool(
                name="CTAOptimizer",
                func=self._optimize_cta_wrapper,
                description="Optimize call-to-action for better response rates. Input should contain body, current CTA, and prospect profile."
            ),
            Tool(
                name="SpamScoreChecker",
                func=self._check_spam_score_wrapper,
                description="Check spam score of email content. Input should contain subject and body."
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

        logger.info("Content Optimizer Agent initialized")

    def _optimize_content_wrapper(self, query: str) -> str:
        """Wrapper for content optimization."""
        try:
            # Parse input - expected format: "subject||body"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 2:
                subject, body = parts[0], parts[1]
            else:
                # Fallback: treat as body only
                subject = "No subject provided"
                body = query

            # Use LLM to optimize content
            prompt = ContentOptimizerPrompts.get_content_optimization_prompt()
            formatted_prompt = prompt.format(subject=subject, body=body)

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error optimizing content: {str(e)}")
            return f"Error optimizing content: {str(e)}"

    def _analyze_readability_wrapper(self, query: str) -> str:
        """Wrapper for readability analysis."""
        try:
            body = query.strip()

            # Use LLM to analyze readability
            prompt = ContentOptimizerPrompts.get_readability_analysis_prompt()
            formatted_prompt = prompt.format(body=body)

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error analyzing readability: {str(e)}")
            return f"Error analyzing readability: {str(e)}"

    def _optimize_cta_wrapper(self, query: str) -> str:
        """Wrapper for CTA optimization."""
        try:
            # Parse input - expected format: "body||current_cta||prospect_profile"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 3:
                body, current_cta, prospect_profile = parts[0], parts[1], parts[2]
            else:
                # Fallback values
                body = query
                current_cta = "Let me know if you're interested"
                prospect_profile = "Technology professional"

            # Use LLM to optimize CTA
            prompt = ContentOptimizerPrompts.get_cta_optimization_prompt()
            formatted_prompt = prompt.format(
                body=body,
                current_cta=current_cta,
                prospect_profile=prospect_profile
            )

            messages = [SystemMessage(content=formatted_prompt)]
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            logger.error(f"Error optimizing CTA: {str(e)}")
            return f"Error optimizing CTA: {str(e)}"

    def _check_spam_score_wrapper(self, query: str) -> str:
        """Wrapper for spam score checking."""
        try:
            # Parse input - expected format: "subject||body"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 2:
                subject, body = parts[0], parts[1]
            else:
                # Fallback: treat as body only
                subject = "No subject"
                body = query

            # Use spam checker tool
            result = self.spam_checker.check_spam_score(subject, body)
            return f"Spam Check Results:\nSpam Score: {result.spam_score}\nLikely Spam: {result.is_likely_spam}\nFactors: {result.factors}\nRecommendations: {result.recommendations}"

        except Exception as e:
            logger.error(f"Error checking spam score: {str(e)}")
            return f"Error checking spam score: {str(e)}"

    def optimize_email(self,
                      subject: str,
                      body: str,
                      prospect_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Optimize email content for better performance.

        Args:
            subject: Email subject line
            body: Email body content
            prospect_profile: Optional prospect information for CTA optimization

        Returns:
            Dictionary containing optimized content and analysis
        """
        logger.info("Optimizing email content")

        try:
            # Optimize overall content
            content_input = f"{subject}||{body}"
            optimization_result = self._optimize_content_wrapper(content_input)

            # Analyze readability
            readability_result = self._analyze_readability_wrapper(body)

            # Optimize CTA (if prospect profile provided)
            cta_result = ""
            if prospect_profile:
                cta_input = f"{body}||Let me know if you're interested||{self._format_dict_for_prompt(prospect_profile)}"
                cta_result = self._optimize_cta_wrapper(cta_input)

            # Check spam score
            spam_result = self._check_spam_score_wrapper(f"{subject}||{body}")

            # Parse results to extract optimized content
            parsed_results = self._parse_optimization_results(
                optimization_result, readability_result, cta_result, spam_result
            )

            result = {
                "optimized_subject": parsed_results.get("optimized_subject", subject),
                "optimized_body": parsed_results.get("optimized_body", body),
                "readability_analysis": readability_result,
                "cta_optimization": cta_result,
                "spam_analysis": spam_result,
                "optimization_details": optimization_result,
                "original_subject": subject,
                "original_body": body,
                "optimization_timestamp": self._get_timestamp()
            }

            logger.info("Email optimization completed")
            return result

        except Exception as e:
            logger.error(f"Error optimizing email: {str(e)}")
            return {
                "error": str(e),
                "original_subject": subject,
                "original_body": body,
                "optimization_timestamp": self._get_timestamp()
            }

    def _parse_optimization_results(self,
                                  optimization: str,
                                  readability: str,
                                  cta: str,
                                  spam: str) -> Dict[str, Any]:
        """Parse optimization results to extract key improvements."""
        results = {
            "optimized_subject": "",
            "optimized_body": ""
        }

        try:
            # Extract optimized subject from optimization result
            lines = optimization.split('\n')
            for i, line in enumerate(lines):
                if "Optimized subject line:" in line or "Subject:" in line:
                    # Get the next line or same line after colon
                    if ":" in line:
                        potential_subject = line.split(":", 1)[1].strip()
                        if potential_subject and len(potential_subject) < 100:
                            results["optimized_subject"] = potential_subject
                    elif i + 1 < len(lines):
                        potential_subject = lines[i + 1].strip()
                        if potential_subject and len(potential_subject) < 100:
                            results["optimized_subject"] = potential_subject
                    break

            # Extract optimized body from optimization result
            for i, line in enumerate(lines):
                if "Optimized email body:" in line or "Body:" in line:
                    # Collect subsequent lines as body
                    body_lines = []
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(("Readability", "Spam", "CTA", "Explanation")):
                            body_lines.append(lines[j])
                        elif body_lines:  # Stop when we hit a section header after collecting content
                            break
                    if body_lines:
                        results["optimized_body"] = '\n'.join(body_lines).strip()
                    break

            # If we didn't find structured optimization, use original
            if not results["optimized_subject"]:
                results["optimized_subject"] = ""  # Will be filled by fallback
            if not results["optimized_body"]:
                results["optimized_body"] = ""  # Will be filled by fallback

        except Exception as e:
            logger.error(f"Error parsing optimization results: {str(e)}")

        return results

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

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_optimization_summary(self, optimization_data: Dict[str, Any]) -> str:
        """Get a formatted summary of the optimization results."""
        if "error" in optimization_data:
            return f"Optimization Error: {optimization_data['error']}"

        summary_parts = []

        summary_parts.append(f"Original Subject: {optimization_data.get('original_subject', 'N/A')}")
        summary_parts.append(f"Optimized Subject: {optimization_data.get('optimized_subject', 'N/A')}")
        summary_parts.append("")
        summary_parts.append(f"Original Body Length: {len(optimization_data.get('original_body', ''))} characters")
        summary_parts.append(f"Optimized Body Length: {len(optimization_data.get('optimized_body', ''))} characters")

        if optimization_data.get('spam_analysis'):
            summary_parts.append("")
            summary_parts.append("Spam Analysis: Available (see full results)")

        return "\n".join(summary_parts)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = ContentOptimizerAgent()

    # Test with sample email
    subject = "Following up on our conversation"
    body = """Hi John,

It was great speaking with you last week about Acme Corp's expansion plans.
I wanted to follow up and see if you had any questions about the proposal I sent over.

Our solution has helped companies like yours reduce operational costs by 25% while improving team productivity.

Would you have 15 minutes for a quick call this week to discuss next steps?

Best regards,
Sarah Johnson"""

    prospect_profile = {
        "full_name": "John Doe",
        "title": "VP of Engineering",
        "company": "Acme Corp"
    }

    optimization_result = agent.optimize_email(subject, body, prospect_profile)
    print("Optimization Results:")
    print(agent.get_optimization_summary(optimization_result))