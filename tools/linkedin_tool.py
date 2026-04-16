"""
LinkedIn Tool for mock LinkedIn profile and company data extraction.
Provides simulated LinkedIn scraping capabilities for research purposes.
"""

import re
import random
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LinkedInTool:
    """Tool for extracting LinkedIn profile and company information (mock)."""

    def __init__(self):
        # Mock data pools
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
            "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
            "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
            "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"
        ]

        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
            "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"
        ]

        self.titles = [
            "CEO", "Founder", "CTO", "Chief Technology Officer",
            "VP of Engineering", "Director of Engineering",
            "VP of Sales", "Director of Sales", "Sales Manager",
            "VP of Marketing", "Director of Marketing", "Marketing Manager",
            "Product Manager", "Senior Product Manager", "Director of Product",
            "COO", "Chief Operating Officer", "VP of Operations",
            "CFO", "Chief Financial Officer", "VP of Finance",
            "HR Director", "People Operations Manager", "HR Manager"
        ]

        self.companies = [
            "Innovatech Solutions", "Global Dynamics Inc", "TechCorp Industries",
            "DataSystems LLC", "CloudWorks Technologies", "NextGen Innovations",
            "FutureLabs Inc", "Apex Dynamics Group", "Nexus Technologies",
            "Vertex Solutions", "Quantum Leap Tech", "Nova Systems",
            "Orbit Technologies", "Pinnacle Performance", "Summit Consulting",
            "Peak Performance Inc", "Elite Strategies LLC", "Prime Technologies"
        ]

        self.industries = [
            "Information Technology", "Software Development", "Financial Services",
            "Healthcare", "Retail & E-commerce", "Manufacturing",
            "Professional Services", "Education", "Real Estate",
            "Marketing & Advertising", "Consulting", "Telecommunications"
        ]

        self.locations = [
            "San Francisco Bay Area", "New York City", "Austin, TX",
            "Boston, MA", "Seattle, WA", "Los Angeles, CA",
            "Chicago, IL", "Denver, CO", "Atlanta, GA",
            "Remote", "London, UK", "Toronto, Canada",
            "Berlin, Germany", "Sydney, Australia", "Singapore"
        ]

        self.skills_pool = [
            "Leadership", "Strategic Planning", "Team Management",
            "Project Management", "Budget Management", "Sales Strategy",
            "Marketing Strategy", "Product Development", "Customer Relations",
            "Data Analysis", "Problem Solving", "Communication",
            "Negotiation", "Public Speaking", "Microsoft Office",
            "Salesforce", "HubSpot", "Google Analytics", "SQL", "Python",
            "JavaScript", "React", "Node.js", "AWS", "Azure", "Docker"
        ]

        self.schools = [
            "Stanford University", "MIT", "Harvard University", "UC Berkeley",
            "Carnegie Mellon University", "University of Texas at Austin",
            "New York University", "Georgetown University", "Northwestern University",
            "University of Michigan", "UCLA", "University of Washington",
            "Georgia Tech", "University of Illinois", "Texas A&M University"
        ]

        self.degrees = [
            "Bachelor of Science", "Bachelor of Arts", "Master of Business Administration",
            "Master of Science", "Bachelor of Engineering", "Doctor of Philosophy",
            "Master of Arts", "Bachelor of Business Administration"
        ]

    def extract_profile_info(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Extract profile information from LinkedIn URL (mock implementation).

        Args:
            linkedin_url: LinkedIn profile URL

        Returns:
            Dictionary containing profile information
        """
        logger.info(f"Extracting LinkedIn profile info from: {linkedin_url}")

        # Validate URL format
        if not self._is_valid_linkedin_url(linkedin_url):
            logger.warning(f"Invalid LinkedIn URL format: {linkedin_url}")
            return self._get_unknown_profile()

        # Generate mock profile data
        profile = self._generate_mock_profile()

        # Add URL to profile
        profile["linkedin_url"] = linkedin_url
        profile["extraction_date"] = datetime.now().isoformat()
        profile["data_source"] = "Mock LinkedIn Scraper"

        logger.info(f"Generated mock profile for: {profile['full_name']}")
        return profile

    def extract_company_info(self, company_name: str) -> Dict[str, Any]:
        """
        Extract company information (mock implementation).

        Args:
            company_name: Name of the company

        Returns:
            Dictionary containing company information
        """
        logger.info(f"Extracting company info for: {company_name}")

        company_info = {
            "name": company_name,
            "industry": random.choice(self.industries),
            "size": self._estimate_company_size(company_name),
            "founded_year": self._estimate_founded_year(company_name),
            "headquarters": random.choice(self.locations),
            "description": self._generate_company_description(company_name),
            "specialties": random.sample(self.skills_pool, k=random.randint(3, 6)),
            "employee_count_estimate": self._get_employee_count_range(
                self._estimate_company_size(company_name)
            ),
            "extraction_date": datetime.now().isoformat(),
            "data_source": "Mock LinkedIn Company Scraper"
        }

        return company_info

    def search_prospects_by_company(
        self,
        company_name: str,
        title_keywords: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for prospects at a specific company (mock implementation).

        Args:
            company_name: Company name to search within
            title_keywords: Optional list of title keywords to filter by
            limit: Maximum number of results to return

        Returns:
            List of prospect profiles
        """
        logger.info(f"Searching for prospects at {company_name}")

        prospects = []
        num_prospects = min(limit, random.randint(3, 8))

        for i in range(num_prospects):
            prospect = self._generate_mock_profile(company_name=company_name)
            prospect["linkedin_url"] = f"https://linkedin.com/in/{self._generate_linkedin_id()}"

            # Filter by title keywords if provided
            if title_keywords:
                title_lower = prospect["title"].lower()
                if not any(keyword.lower() in title_lower for keyword in title_keywords):
                    continue

            prospects.append(prospect)

        return prospects

    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format."""
        linkedin_patterns = [
            r'^https?://(www\.)?linkedin\.com/in/[\w\-]+/?$',
            r'^https?://(www\.)?linkedin\.com/pub/[\w\-]+/\d+/\d+/\d+/?$'
        ]
        return any(re.match(pattern, url) for pattern in linkedin_patterns)

    def _generate_mock_profile(self, company_name: Optional[str] = None) -> Dict[str, Any]:
        """Generate a mock LinkedIn profile."""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        full_name = f"{first_name} {last_name}"

        # Use provided company or select random one
        company = company_name if company_name else random.choice(self.companies)

        profile = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "title": random.choice(self.titles),
            "company": company,
            "industry": random.choice(self.industries),
            "location": random.choice(self.locations),
            "experience_years": random.randint(2, 25),
            "education": self._generate_education(),
            "skills": random.sample(self.skills_pool, k=random.randint(4, 8)),
            "connections": random.randint(50, 800),
            "followers": random.randint(100, 2000),
            "summary": self._generate_professional_summary(first_name, company),
            "recent_activity": self._generate_recent_activity(),
            "featured": self._generate_featured_content()
        }

        return profile

    def _generate_education(self) -> List[Dict[str, Any]]:
        """Generate mock education background."""
        education = []
        num_degrees = random.randint(1, 2)

        for _ in range(num_degrees):
            school = random.choice(self.schools)
            degree = random.choice(self.degrees)
            graduation_year = random.randint(2005, 2020)

            education.append({
                "school": school,
                "degree": degree,
                "graduation_year": graduation_year,
                "field_of_study": self._get_field_for_degree(degree)
            })

        return education

    def _get_field_for_degree(self, degree: str) -> str:
        """Get appropriate field of study for degree."""
        fields = {
            "Bachelor of Science": ["Computer Science", "Engineering", "Mathematics", "Physics"],
            "Bachelor of Arts": ["Economics", "Psychology", "Communications", "English"],
            "Master of Business Administration": ["Business Administration", "Finance", "Marketing"],
            "Master of Science": ["Computer Science", "Data Science", "Engineering", "Finance"],
            "Bachelor of Engineering": ["Software Engineering", "Mechanical Engineering", "Electrical Engineering"],
            "Doctor of Philosophy": ["Computer Science", "Engineering", "Physics", "Mathematics"],
            "Master of Arts": ["Psychology", "Communications", "Education", "History"],
            "Bachelor of Business Administration": ["Business Administration", "Finance", "Marketing", "Management"]
        }
        return random.choice(fields.get(degree, ["Business", "Technology"]))

    def _generate_professional_summary(self, first_name: str, company: str) -> str:
        """Generate a mock professional summary."""
        summaries = [
            f"Results-driven {random.choice(self.titles).lower()} with {random.randint(5, 15)} years of experience driving growth and innovation at {company}. Passionate about leveraging technology to solve complex business challenges.",
            f"Strategic leader specializing in {random.choice(['product development', 'sales strategy', 'market expansion', 'operational efficiency'])}. Dedicated to building high-performing teams and delivering exceptional customer value.",
            f"Experienced professional with expertise in {random.choice(['digital transformation', 'business strategy', 'technology leadership', 'customer success'])}. Proven track record of delivering measurable results in fast-paced environments.",
            f"Dynamic {random.choice(self.titles).lower()} focused on {random.choice(['innovation', 'growth', 'efficiency', 'transformation'])}. Adept at bridging the gap between technology and business objectives."
        ]
        return random.choice(summaries)

    def _generate_recent_activity(self) -> List[Dict[str, Any]]:
        """Generate mock recent LinkedIn activity."""
        activities = [
            {
                "type": "post",
                "content": f"Excited to share that {random.choice(self.companies)} just announced a new partnership that will enhance our capabilities in {random.choice(['AI', 'cloud computing', 'data analytics'])}.",
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat(),
                "engagement": random.randint(5, 50)
            },
            {
                "type": "article",
                "content": f"Insights on {random.choice(['leadership in tech', 'future of work', 'digital innovation'])} and how organizations can adapt to changing market dynamics.",
                "timestamp": (datetime.now() - timedelta(days=random.randint(8, 30))).isoformat(),
                "engagement": random.randint(10, 100)
            },
            {
                "type": "comment",
                "content": f"Great perspective on {random.choice(['remote work', 'AI ethics', 'sustainable business'])}. I've found that {random.choice(['clear communication', 'data-driven decisions', 'continuous learning'])} is key.",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                "engagement": random.randint(2, 15)
            }
        ]
        return random.sample(activities, k=random.randint(1, 3))

    def _generate_featured_content(self) -> List[Dict[str, Any]]:
        """Generate mock featured content."""
        featured = [
            {
                "type": "project",
                "title": f"Led {random.choice(['digital transformation', 'product launch', 'market expansion'])} initiative",
                "description": f"Directed cross-functional team of {random.randint(5, 20)} to deliver {random.choice(['$2M+', '$5M+', '$10M+'])} in value through {random.choice(['process optimization', 'technology modernization', 'customer experience enhancement'])}.",
                "duration": f"{random.randint(6, 24)} months"
            },
            {
                "type": "certification",
                "name": random.choice(["PMP", "AWS Solutions Architect", "Google Cloud Professional", "Scrum Master", "TOGAF"]),
                "issuer": random.choice(["PMI", "Amazon Web Services", "Google Cloud", "Scrum Alliance", "The Open Group"]),
                "date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()[:10]
            }
        ]
        return random.sample(featured, k=random.randint(1, 2))

    def _generate_company_description(self, company_name: str) -> str:
        """Generate mock company description."""
        descriptors = [
            "a leading provider of innovative solutions",
            "specializing in cutting-edge technology",
            "dedicated to helping businesses thrive",
            "at the forefront of industry innovation",
            "committed to delivering exceptional value",
            "focused on driving sustainable growth",
            "passionate about solving complex challenges",
            "empowering organizations through technology"
        ]
        return f"{company_name} is {random.choice(descriptors)} in the {random.choice(self.industries)} sector."

    def _estimate_company_size(self, company_name: str) -> str:
        """Estimate company size based on name characteristics."""
        # Simple heuristic based on name length and complexity
        if len(company_name) > 20 or company_name.count(' ') > 2:
            return random.choice(["201-500 employees", "501-1000 employees", "1000+ employees"])
        elif len(company_name) > 15:
            return random.choice(["51-200 employees", "201-500 employees"])
        else:
            return random.choice(["1-10 employees", "11-50 employees", "51-200 employees"])

    def _estimate_founded_year(self, company_name: str) -> int:
        """Estimate founded year."""
        current_year = datetime.now().year
        # Estimate based on name (older-sounding names get earlier dates)
        if any(word in company_name.lower() for word ['group', 'corporation', 'industries', 'company']):
            return random.randint(1980, 2005)
        else:
            return random.randint(2005, 2020)

    def _get_employee_count_range(self, size_str: str) -> str:
        """Convert size string to employee count range."""
        size_map = {
            "1-10 employees": "1-10",
            "11-50 employees": "11-50",
            "51-200 employees": "51-200",
            "201-500 employees": "201-500",
            "501-1000 employees": "501-1000",
            "1000+ employees": "1000+"
        }
        return size_map.get(size_str, "51-200")

    def _generate_linkedin_id(self) -> str:
        """Generate a mock LinkedIn ID."""
        first = random.choice(self.first_names).lower()
        last = random.choice(self.last_names).lower()
        num = random.randint(10, 99)
        return f"{first}-{last}-{num}"

    def _get_unknown_profile(self) -> Dict[str, Any]:
        """Return unknown profile for invalid URLs."""
        return {
            "error": "Invalid LinkedIn URL",
            "full_name": "Unknown Person",
            "title": "Unknown Position",
            "company": "Unknown Company",
            "linkedin_url": "",
            "extraction_date": datetime.now().isoformat(),
            "data_source": "Mock LinkedIn Scraper"
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    tool = LinkedInTool()

    # Test profile extraction
    profile = tool.extract_profile_info("https://linkedin.com/in/johndoe")
    print("LinkedIn Profile:")
    for key, value in profile.items():
        if key not in ['education', 'skills', 'recent_activity', 'featured']:
            print(f"  {key}: {value}")

    print("\n" + "="*50 + "\n")

    # Test company info
    company_info = tool.extract_company_info("Innovatech Solutions")
    print("Company Info:")
    for key, value in company_info.items():
        print(f"  {key}: {value}")

    print("\n" + "="*50 + "\n")

    # Test prospect search
    prospects = tool.search_prospects_by_company("TechCorp Industries", title_keywords=["VP", "Director"], limit=5)
    print(f"Found {len(prospects)} prospects:")
    for i, prospect in enumerate(prospects, 1):
        print(f"  {i}. {prospect['full_name']} - {prospect['title']} at {prospect['company']}")