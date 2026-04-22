"""
Scheduler Agent for determining optimal email sending times.
Handles scheduling logic and integrates with email sending.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pytz
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool

from tools.email_tool import EmailTool, EmailConfig

logger = logging.getLogger(__name__)

class SchedulerAgent:
    """Agent responsible for scheduling email sends at optimal times."""

    def __init__(self, llm_model: str = "gpt-3.5-turbo", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=llm_model, temperature=temperature)
        self.email_tool = EmailTool()

        # Initialize tools for the agent
        self.tools = [
            Tool(
                name="OptimalTimeCalculator",
                func=self._calculate_optimal_time_wrapper,
                description="Calculate optimal time to send email based on prospect timezone and habits. Input should contain prospect profile and timezone info."
            ),
            Tool(
                name="ScheduleEmailSender",
                func=self._schedule_email_wrapper,
                description="Schedule an email to be sent at a specific time. Input should contain email details and send time."
            ),
            Tool(
                name="BestDayAnalyzer",
                func=self._analyze_best_day_wrapper,
                description="Analyze which day of week is best for sending to a prospect. Input should contain prospect profile and industry."
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

        logger.info("Scheduler Agent initialized")

    def _calculate_optimal_time_wrapper(self, query: str) -> str:
        """Wrapper for optimal time calculation."""
        try:
            # Parse input - expected format: "prospect_profile||timezone"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 2:
                prospect_profile, timezone_str = parts[0], parts[1]
            else:
                # Fallback values
                prospect_profile = query
                timezone_str = "UTC"

            # Calculate optimal time
            optimal_time = self._calculate_optimal_send_time(prospect_profile, timezone_str)
            return f"Optimal Send Time: {optimal_time}"

        except Exception as e:
            logger.error(f"Error calculating optimal time: {str(e)}")
            return f"Error calculating optimal time: {str(e)}"

    def _schedule_email_wrapper(self, query: str) -> str:
        """Wrapper for scheduling email sending."""
        try:
            # Parse input - expected format: "to_email||subject||body||send_time"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 4:
                to_email, subject, body, send_time_str = parts[0], parts[1], parts[2], parts[3]
            else:
                # Fallback values
                to_email = "test@example.com"
                subject = query
                body = "Email body"
                send_time_str = datetime.now().isoformat()

            # Parse send time
            try:
                send_time = datetime.fromisoformat(send_time_str.replace('Z', '+00:00'))
            except:
                send_time = datetime.now()

            # Send email (in real implementation, this would be truly scheduled)
            # For now, we'll send immediately but track the intended time
            result = self.email_tool.send_email(to_email, subject, body)
            return f"Email sent at {send_time}: {result.success} - {result.message_id or result.error}"

        except Exception as e:
            logger.error(f"Error scheduling email: {str(e)}")
            return f"Error scheduling email: {str(e)}"

    def _analyze_best_day_wrapper(self, query: str) -> str:
        """Wrapper for analyzing best day to send."""
        try:
            # Parse input - expected format: "prospect_profile||industry"
            parts = [part.strip() for part in query.split('||')]
            if len(parts) >= 2:
                prospect_profile, industry = parts[0], parts[1]
            else:
                # Fallback values
                prospect_profile = query
                industry = "technology"

            # Analyze best day
            best_day = self._analyze_best_send_day(prospect_profile, industry)
            return f"Best Day to Send: {best_day}"

        except Exception as e:
            logger.error(f"Error analyzing best day: {str(e)}")
            return f"Error analyzing best day: {str(e)}"

    def schedule_email(self,
                      prospect_profile: Dict[str, Any],
                      subject: str,
                      body: str,
                      timezone: Optional[str] = None) -> Dict[str, Any]:
        """
        Schedule an email to be sent at an optimal time.

        Args:
            prospect_profile: Information about the prospect
            subject: Email subject line
            body: Email body content
            timezone: Prospect's timezone (if known)

        Returns:
            Dictionary containing scheduling details and result
        """
        logger.info("Scheduling email for optimal send time")

        try:
            # Determine prospect timezone if not provided
            if not timezone:
                timezone = self._extract_timezone(prospect_profile)

            # Calculate optimal send time
            optimal_time = self._calculate_optimal_send_time(prospect_profile, timezone)

            # Determine best day if needed
            best_day = self._analyze_best_send_day(prospect_profile,
                                                  prospect_profile.get("industry", "technology"))

            # Prepare email for sending
            to_email = prospect_profile.get("email", "test@example.com")

            # Send email (in production, this would be queued for actual scheduling)
            email_result = self.email_tool.send_email(to_email, subject, body)

            result = {
                "prospect_profile": prospect_profile,
                "subject": subject,
                "body": body,
                "timezone": timezone,
                "calculated_optimal_time": optimal_time,
                "best_day_recommendation": best_day,
                "actual_send_time": datetime.now().isoformat(),  # When we actually sent it
                "intended_send_time": optimal_time,  # When we intended to send it
                "email_result": {
                    "success": email_result.success,
                    "message_id": email_result.message_id,
                    "error": email_result.error,
                    "attempts": email_result.attempts
                },
                "scheduling_timestamp": self._get_timestamp()
            }

            logger.info(f"Email scheduled and sent to {to_email}")
            return result

        except Exception as e:
            logger.error(f"Error scheduling email: {str(e)}")
            return {
                "error": str(e),
                "scheduling_timestamp": self._get_timestamp()
            }

    def _extract_timezone(self, prospect_profile: Dict[str, Any]) -> str:
        """Extract timezone from prospect profile or infer from location."""
        # Try to get timezone from profile
        if "timezone" in prospect_profile:
            return prospect_profile["timezone"]

        # Try to infer from location
        location = prospect_profile.get("location", "").lower()
        if "san francisco" in location or "pacific" in location:
            return "America/Los_Angeles"
        elif "new york" in location or "eastern" in location:
            return "America/New_York"
        elif "chicago" in location or "central" in location:
            return "America/Chicago"
        elif "denver" in location or "mountain" in location:
            return "America/Denver"
        elif "london" in location or "uk" in location:
            return "Europe/London"
        elif "toronto" in location or "canada" in location:
            return "America/Toronto"
        else:
            # Default to UTC if unknown
            return "UTC"

    def _calculate_optimal_send_time(self, prospect_profile: Dict[str, Any], timezone_str: str) -> str:
        """Calculate optimal time to send email based on prospect habits."""
        try:
            # Get timezone object
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            # Default optimal times (Tuesday-Thursday, 10 AM - 2 PM local time)
            # Adjust based on prospect role and industry
            title = prospect_profile.get("title", "").lower()
            industry = prospect_profile.get("industry", "").lower()

            # Base optimal time: 10:30 AM local time
            optimal_hour = 10
            optimal_minute = 30

            # Adjust based on role
            if any(role in title for role in ["ceo", "founder", "president"]):
                # Executives often check email early morning or late evening
                optimal_hour = 8  # 8 AM
            elif any(role in title for role in ["developer", "engineer", "programmer"]):
                # Engineers might prefer later morning
                optimal_hour = 11  # 11 AM
            elif any(role in title for role in ["sales", "marketing"]):
                # Sales/Marketing often check throughout day
                optimal_hour = 10  # 10 AM
            elif any(role in title for role in ["hr", "recruiter"]):
                # HR often checks during business hours
                optimal_hour = 9  # 9 AM

            # Adjust based on industry
            if "finance" in industry or "banking" in industry:
                # Finance professionals start early
                optimal_hour = max(optimal_hour - 1, 7)
            elif "technology" in industry or "software" in industry:
                # Tech workers might be flexible
                pass  # Keep as is
            elif "healthcare" in industry:
                # Healthcare workers have varied schedules
                optimal_hour = 12  # Noon
            elif "retail" in industry:
                # Retail workers might check before/after shifts
                optimal_hour = 8  # 8 AM

            # Create optimal datetime for today
            optimal_time = now.replace(hour=optimal_hour, minute=optimal_minute, second=0, microsecond=0)

            # If optimal time has passed today, schedule for tomorrow
            if optimal_time <= now:
                optimal_time += timedelta(days=1)

            # Avoid weekends if possible (unless prospect is known to work weekends)
            if optimal_time.weekday() >= 5:  # Saturday=5, Sunday=6
                # Move to next Monday
                days_ahead = 7 - optimal_time.weekday()
                optimal_time += timedelta(days=days_ahead)

            return optimal_time.isoformat()

        except Exception as e:
            logger.error(f"Error calculating optimal send time: {str(e)}")
            # Fallback: send in 1 hour
            return (datetime.now() + timedelta(hours=1)).isoformat()

    def _analyze_best_send_day(self, prospect_profile: Dict[str, Any], industry: str) -> str:
        """Analyze which day of week is best for sending to prospect."""
        try:
            title = prospect_profile.get("title", "").lower()

            # General best days: Tuesday, Wednesday, Thursday
            # Adjust based on role and industry
            if any(role in title for role in ["ceo", "founder", "president", "vp"]):
                # Executives often prefer mid-week
                return "Wednesday"
            elif any(role in title for role in ["developer", "engineer", "programmer"]):
                # Engineers often prefer Tuesday or Wednesday
                return "Tuesday"
            elif any(role in title for role in ["sales", "marketing", "business development"]):
                # Sales/Marketing often do well mid-week
                return "Wednesday"
            elif any(role in title for role in ["hr", "recruiter", "people"]):
                # HR often prefers Tuesday-Thursday
                return "Thursday"
            else:
                # Default best practice
                return "Wednesday"

        except Exception as e:
            logger.error(f"Error analyzing best send day: {str(e)}")
            return "Wednesday"

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_scheduling_summary(self, schedule_data: Dict[str, Any]) -> str:
        """Get a formatted summary of the scheduling details."""
        if "error" in schedule_data:
            return f"Scheduling Error: {schedule_data['error']}"

        summary_parts = []

        summary_parts.append(f"Prospect: {schedule_data.get('prospect_profile', {}).get('full_name', 'Unknown')}")
        summary_parts.append(f"Subject: {schedule_data.get('subject', 'No subject')}")
        summary_parts.append(f"Timezone: {schedule_data.get('timezone', 'Unknown')}")
        summary_parts.append(f"Calculated Optimal Time: {schedule_data.get('calculated_optimal_time', 'N/A')}")
        summary_parts.append(f"Best Day Recommendation: {schedule_data.get('best_day_recommendation', 'N/A')}")
        summary_parts.append(f"Actual Send Time: {schedule_data.get('actual_send_time', 'N/A')}")
        summary_parts.append(f"Email Sent Successfully: {schedule_data.get('email_result', {}).get('success', False)}")

        if not schedule_data.get('email_result', {}).get('success', False):
            summary_parts.append(f"Error: {schedule_data.get('email_result', {}).get('error', 'Unknown error')}")

        return "\n".join(summary_parts)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize agent
    agent = SchedulerAgent()

    # Test with sample prospect
    sample_prospect = {
        "full_name": "John Doe",
        "title": "VP of Engineering",
        "company": "Acme Corp",
        "industry": "technology",
        "location": "San Francisco, CA",
        "email": "john.doe@acmecorp.com"
    }

    subject = "Quick question about Acme Corp's engineering challenges"
    body = """Hi John,

I noticed Acme Corp recently launched an AI-powered product and secured Series B funding - congratulations!

I work with engineering leaders like you to help scale teams efficiently while reducing operational costs.

Would you be open to a brief 15-minute call next week to share how we've helped similar companies?

Best regards,
Sarah Johnson"""

    # Schedule email
    schedule_result = agent.schedule_email(sample_prospect, subject, body)
    print("Scheduling Results:")
    print(agent.get_scheduling_summary(schedule_result))