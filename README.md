# AI Cold Email Outreach System

An intelligent multi-agent system for personalized cold email outreach using LangChain.

## Features

- Research Agent: Gathers company/prospect information
- Personalization Agent: Builds detailed prospect profiles
- Email Writer Agent: Creates personalized cold emails using proven frameworks
- Content Optimizer Agent: Improves subject lines, readability, and CTA
- Scheduler Agent: Handles email timing and delivery
- Memory Agent: Stores interactions for continuous improvement using FAISS vector database

## Project Structure

```
agents/
- research_agent.py
- personalization_agent.py
- email_writer_agent.py
- content_optimizer_agent.py
- scheduler_agent.py
- memory_agent.py

tools/
- research_tool.py
- email_tool.py
- spam_checker_tool.py
- linkedin_tool.py

prompts/
- research_prompt.py
- personalization_prompt.py
- email_writer_prompt.py
- content_optimizer_prompt.py

memory/
- faiss_index/

main.py
requirements.txt
.env.example
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```
5. Run the system:
   ```bash
   python main.py
   ```

## Usage Example

```python
from main import ColdEmailSystem

# Initialize the system
system = ColdEmailSystem()

# Process a new lead
lead_data = {
    "name": "John Doe",
    "company": "Acme Corp",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "position": "CEO"
}

result = system.process_lead(lead_data)
print(result)
```

## Modules Overview

### Agents
- **Research Agent**: Uses web search and LinkedIn data to gather company news, industry trends, and pain points
- **Personalization Agent**: Analyzes prospect role and company to identify specific challenges and opportunities
- **Email Writer Agent**: Generates emails using AIDA (Attention, Interest, Desire, Action) or PAS (Problem, Agitate, Solution) frameworks
- **Content Optimizer Agent**: Optimizes subject lines for open rates, checks spam score, and improves readability
- **Scheduler Agent**: Determines optimal send times based on prospect timezone and historical engagement data
- **Memory Agent**: Stores successful/failed interactions in FAISS vector store for continuous learning

### Tools
- Research Tool: Mock LinkedIn scraping and company research
- Email Tool: SMTP-based email sending with retry logic
- Spam Checker: Heuristic-based spam score calculation
- LinkedIn Tool: Simulated LinkedIn data extraction

## Extending the System

- Add real LinkedIn scraping with Apify or PhantomBuster
- Integrate with email marketing platforms (SendGrid, Mailgun)
- Add A/B testing framework for subject lines
- Implement email open/click tracking
- Add more sophisticated pain point analysis using NLP

## Requirements

- Python 3.8+
- LangChain
- OpenAI API key
- FAISS or Chroma vector store
- SMTP server for email sending

## Disclaimer

This system is for educational purposes. Always comply with anti-spam laws (CAN-SPAM, GDPR) when sending cold emails.