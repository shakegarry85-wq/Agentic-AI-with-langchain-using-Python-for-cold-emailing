"""
Research Tool for gathering company and prospect information.
Provides mock research capabilities that can be extended with real web scraping.
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ResearchTool:
    """Tool for researching companies and prospects."""

    def __init__(self):
        self.mock_data = {
            "tech": [
                "recently launched a new AI-powered product",
                "secured Series B funding round",
                "expanding into European markets",
                "facing increased competition from startups",
                "implementing cost-cutting measures",
                "hiring aggressively for engineering roles",
                "struggling with customer churn",
                "planning IPO for next year"
            ],
            "finance": [
                "reporting strong Q3 earnings",
                "facing regulatory scrutiny",
                "launching new digital banking platform",
                "acquiring smaller fintech startup",
                "dealing with market volatility",
                "implementing new risk management systems",
                "expanding wealth management services",
                "cutting back on trading desk"
            ],
            "healthcare": [
                "receiving FDA approval for new device",
                "facing supply chain disruptions",
                "expanding telehealth services",
                "dealing with staffing shortages",
                "launching patient portal improvements",
                "partnering with research institutions",
                "implementing electronic health records",
                "facing reimbursement pressure"
            ],
            "retail": [
                "experiencing strong holiday sales",
                "facing inventory management challenges",
                "launching e-commerce platform improvements",
                "dealing with changing consumer preferences",
                "expanding into new geographic markets",
                "implementing omnichannel strategy",
                "struggling with returns management",
                "investing in sustainability initiatives"
            ]
        }

        self.pain_points = [
            "scaling operations efficiently",
            "reducing customer acquisition costs",
            "improving employee retention",
            "modernizing legacy systems",
            "competing with new entrants",
            "managing remote work productivity",
            "adapting to regulatory changes",
            "improving data-driven decision making",
            "optimizing marketing ROI",
            "enhancing cybersecurity measures"
        ]

    def research_company(self, company_name: str, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Research a company and return relevant information.

        Args:
            company_name: Name of the company to research
            industry: Optional industry classification

        Returns:
            Dictionary containing research findings
        """
        logger.info(f"Researching company: {company_name}")

        # Try to infer industry if not provided
        if not industry:
            industry = self._infer_industry(company_name)

        # Get mock recent news
        recent_news = self._get_mock_recent_news(industry)

        # Get company challenges/pain points
        challenges = self._get_mock_challenges(industry, company_name)

        # Get basic company info
        company_info = {
            "name": company_name,
            "industry": industry,
            "size": self._estimate_company_size(company_name),
            "founded": self._estimate_founded_year(company_name),
            "recent_news": recent_news,
            "key_challenges": challenges,
            "research_date": datetime.now().isoformat(),
            "sources": ["Mock research database", "Industry reports", "News analysis"]
        }

        return company_info

    def research_linkedin_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Research a LinkedIn profile (mock implementation).

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Dictionary containing profile information
        """
        logger.info(f"Researching LinkedIn profile: {linkedin_url}")

        # Extract name from URL if possible
        name_match = re.search(r'/in/([^/]+)/?$', linkedin_url)
        name = name_match.group(1).replace('-', ' ').title() if name_match else "Unknown Person"

        # Mock profile data
        profile = {
            "name": name,
            "linkedin_url": linkedin_url,
            "headline": self._generate_mock_headline(name),
            "company": self._generate_mock_company(name),
            "location": self._generate_mock_location(),
            "experience_years": random.randint(5, 20),
            "education": self._generate_mock_education(),
            "skills": random.sample([
                "Leadership", "Strategy", "Operations", "Sales", "Marketing",
                "Finance", "Technology", "Project Management", "Analytics",
                "Communication", "Problem Solving", "Team Building"
            ], k=4),
            "recent_activity": self._generate_mock_recent_activity(),
            "research_date": datetime.now().isoformat()
        }

        return profile

    def _infer_industry(self, company_name: str) -> str:
        """Infer industry from company name (simplified)."""
        name_lower = company_name.lower()

        tech_keywords = ['tech', 'software', 'ai', 'data', 'cloud', 'digital', 'net', 'sys', 'labs']
        finance_keywords = ['bank', 'capital', 'finance', 'invest', 'credit', 'fund', 'trading']
        health_keywords = ['health', 'med', 'bio', 'pharma', 'care', 'clinic', 'hospital']
        retail_keywords = ['shop', 'store', 'mart', 'retail', 'mart', 'goods', 'market']

        if any(keyword in name_lower for keyword in tech_keywords):
            return "technology"
        elif any(keyword in name_lower for keyword in finance_keywords):
            return "finance"
        elif any(keyword in name_lower for keyword in health_keywords):
            return "healthcare"
        elif any(keyword in name_lower for keyword in retail_keywords):
            return "retail"
        else:
            return "technology"  # Default fallback

    def _get_mock_recent_news(self, industry: str) -> list:
        """Get mock recent news based on industry."""
        industry_news = self.mock_data.get(industry.lower(), self.mock_data["tech"])
        # Return 2-3 random news items
        return random.sample(industry_news, k=min(3, len(industry_news)))

    def _get_mock_challenges(self, industry: str, company_name: str) -> list:
        """Get mock challenges based on industry."""
        # Select 2-3 relevant pain points
        return random.sample(self.pain_points, k=random.randint(2, 3))

    def _estimate_company_size(self, company_name: str) -> str:
        """Estimate company size based on name (mock)."""
        size_options = ["Startup (1-50)", "Small (51-200)", "Medium (201-1000)", "Large (1000+)"]
        # Simple heuristic: longer names might be older/larger companies
        if len(company_name) > 15:
            return random.choice(["Medium (201-1000)", "Large (1000+)"])
        elif len(company_name) > 10:
            return random.choice(["Small (51-200)", "Medium (201-1000)"])
        else:
            return random.choice(["Startup (1-50)", "Small (51-200)"])

    def _estimate_founded_year(self, company_name: str) -> int:
        """Estimate founded year (mock)."""
        current_year = datetime.now().year
        # Random year between 2000 and 2020
        return random.randint(2000, 2020)

    def _generate_mock_headline(self, name: str) -> str:
        """Generate mock LinkedIn headline."""
        titles = ["CEO", "Founder", "CTO", "VP of Engineering", "Director of Sales",
                  "Marketing Manager", "Product Lead", "Operations Manager"]
        companies = ["Innovatech", "Global Solutions", "TechCorp", "DataSystems",
                     "CloudWorks", "NextGen", "FutureLabs", "Apex Dynamics"]
        return f"{random.choice(titles)} at {random.choice(companies)}"

    def _generate_mock_company(self, name: str) -> str:
        """Generate mock company name."""
        companies = ["Innovatech Inc", "Global Solutions Ltd", "TechCorp",
                     "DataSystems Corp", "CloudWorks LLC", "NextGen Technologies",
                     "FutureLabs Inc", "Apex Dynamics", "Nexus Group", "Vertex Solutions"]
        return random.choice(companies)

    def _generate_mock_location(self) -> str:
        """Generate mock location."""
        cities = ["San Francisco, CA", "New York, NY", "Austin, TX", "Boston, MA",
                  "Seattle, WA", "Los Angeles, CA", "Chicago, IL", "Denver, CO",
                  "Remote", "London, UK", "Toronto, Canada", "Berlin, Germany"]
        return random.choice(cities)

    def _generate_mock_education(self) -> list:
        """Generate mock education background."""
        schools = ["Stanford University", "MIT", "Harvard University", "UC Berkeley",
                   "Carnegie Mellon", "University of Texas", "NYU", "Georgetown"]
        degrees = ["BS Computer Science", "BA Economics", "MBA", "MS Engineering",
                   "BS Mathematics", "BA Psychology"]
        return [
            {
                "school": random.choice(schools),
                "degree": random.choice(degrees),
                "year": random.randint(2005, 2015)
            }
        ]

    def _generate_mock_recent_activity(self) -> list:
        """Generate mock recent LinkedIn activity."""
        activities = [
            "Shared an article about industry trends",
            "Published a post about leadership",
            "Commented on a connection's post",
            "Celebrated work anniversary",
            "Updated profile picture",
            "Shared company news",
            "Posted about professional development"
        ]
        return random.sample(activities, k=random.randint(1, 3))


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tool = ResearchTool()

    # Test company research
    company_info = tool.research_company("Acme Corp", "technology")
    print("Company Research:")
    print(company_info)

    # Test LinkedIn research
    profile_info = tool.research_linkedin_profile("https://linkedin.com/in/johndoe")
    print("\nLinkedIn Profile:")
    print(profile_info)