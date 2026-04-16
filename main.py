"""
Main application for the AI Cold Email Outreach System.
Ties together all agents and provides a CLI interface.
"""

import logging
import os
import sys
import argparse
from typing import Dict, Any, Optional, List
from datetime import datetime
import csv

# Import all agents
from agents.research_agent import ResearchAgent
from agents.personalization_agent import PersonalizationAgent
from agents.email_writer_agent import EmailWriterAgent
from agents.content_optimizer_agent import ContentOptimizerAgent
from agents.scheduler_agent import SchedulerAgent
from agents.memory_agent import MemoryAgent

from tools.email_tool import EmailTool
from tools.spam_checker_tool import SpamCheckerTool
from tools.linkedin_tool import LinkedInTool
from tools.research_tool import ResearchTool

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cold_email_system.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ColdEmailSystem:
    """Main system that orchestrates all agents for cold email outreach."""

    def __init__(self):
        logger.info("Initializing Cold Email Outreach System")

        # Initialize all agents
        self.research_agent = ResearchAgent()
        self.personalization_agent = PersonalizationAgent()
        self.email_writer_agent = EmailWriterAgent()
        self.content_optimizer_agent = ContentOptimizerAgent()
        self.scheduler_agent = SchedulerAgent()
        self.memory_agent = MemoryAgent()

        # Initialize standalone tools
        self.email_tool = EmailTool()
        self.spam_checker = SpamCheckerTool()
        self.linkedin_tool = LinkedInTool()
        self.research_tool = ResearchTool()

        logger.info("Cold Email Outreach System initialized successfully")

    def process_lead(self,
                    lead_data: Dict[str, Any],
                    optimize_content: bool = True,
                    schedule_send: bool = True,
                    store_in_memory: bool = True) -> Dict[str, Any]:
        """
        Process a single lead through the entire cold email pipeline.

        Args:
            lead_data: Dictionary containing lead information
                      Expected keys: name, company, linkedin_url (optional), position (optional), email (optional)
            optimize_content: Whether to run content optimization
            schedule_send: Whether to schedule and send the email
            store_in_memory: Whether to store the interaction in memory

        Returns:
            Dictionary containing results from each stage
        """
        logger.info(f"Processing lead: {lead_data.get('name', 'Unknown')} at {lead_data.get('company', 'Unknown Company')}")

        pipeline_results = {
            "lead_data": lead_data,
            "stages": {},
            "final_email": None,
            "send_result": None,
            "memory_stored": False,
            "errors": []
        }

        try:
            # Stage 1: Research
            logger.info("Stage 1: Researching prospect")
            research_result = self.research_agent.research_prospect(
                company_name=lead_data.get("company", ""),
                linkedin_url=lead_data.get("linkedin_url"),
                industry=lead_data.get("industry")
            )
            pipeline_results["stages"]["research"] = research_result

            # Stage 2: Personalization
            logger.info("Stage 2: Building prospect profile")
            personalization_result = self.personalization_agent.create_prospect_profile(research_result)
            pipeline_results["stages"]["personalization"] = personalization_result

            # Stage 3: Email Writing
            logger.info("Stage 3: Generating personalized email")
            # Prepare value proposition (in a real system, this would come from config)
            value_proposition = {
                "solution_name": "OptimizePro Solutions",
                "key_benefits": [
                    "Increase operational efficiency by 30%",
                    "Reduce costs by 25%",
                    "Improve team productivity",
                    "Scale without growing headcount"
                ],
                "target_problems": [
                    "Scaling challenges",
                    "High operational costs",
                    "Manual processes",
                    "Inadequate technology stack"
                ],
                "unique_differentiators": [
                    "AI-powered optimization",
                    "Proven ROI within 90 days",
                    "Dedicated customer success team",
                    "No long-term contracts"
                ]
            }

            email_result = self.email_writer_agent.generate_email(
                prospect_profile=personalization_result,
                personalization_insights={},  # Could be extracted from personalization_result
                value_proposition=value_proposition
            )
            pipeline_results["stages"]["email_writing"] = email_result

            # Stage 4: Content Optimization (optional)
            if optimize_content and email_result.get("generated_email"):
                logger.info("Stage 4: Optimizing email content")
                generated_email = email_result["generated_email"]
                subject = generated_email.get("subject", "")
                body = generated_email.get("body", "")

                optimization_result = self.content_optimizer_agent.optimize_email(
                    subject=subject,
                    body=body,
                    prospect_profile=personalization_result
                )
                pipeline_results["stages"]["content_optimization"] = optimization_result

                # Update final email with optimized version
                if not optimization_result.get("error"):
                    pipeline_results["final_email"] = {
                        "subject": optimization_result.get("optimized_subject", subject),
                        "body": optimization_result.get("optimized_body", body)
                    }
                else:
                    pipeline_results["final_email"] = generated_email
            else:
                pipeline_results["final_email"] = email_result.get("generated_email", {})

            # Stage 5: Scheduling and Sending (optional)
            if schedule_send and pipeline_results["final_email"]:
                logger.info("Stage 5: Scheduling and sending email")
                # Extract prospect email from lead data or research
                prospect_email = lead_data.get("email")
                if not prospect_email:
                    # Try to get from research data
                    prospect_email = ""
                    if "linkedin_profile" in research_result:
                        linkedin_data = research_result["linkedin_profile"]
                        if isinstance(linkedin_data, dict):
                            prospect_email = linkedin_data.get("email", "")

                    # If still no email, use a placeholder or skip sending
                    if not prospect_email:
                        logger.warning("No email address found for prospect, skipping send")
                        pipeline_results["send_result"] = {
                            "success": False,
                            "error": "No email address available for prospect"
                        }
                    else:
                        # Send the email
                        send_result = self.scheduler_agent.schedule_email(
                            prospect_profile=personalization_result,
                            subject=pipeline_results["final_email"]["subject"],
                            body=pipeline_results["final_email"]["body"],
                            timezone=lead_data.get("timezone")
                        )
                        pipeline_results["send_result"] = send_result
                else:
                    # Send the email
                    send_result = self.scheduler_agent.schedule_email(
                        prospect_profile=personalization_result,
                        subject=pipeline_results["final_email"]["subject"],
                        body=pipeline_results["final_email"]["body"],
                        timezone=lead_data.get("timezone")
                    )
                    pipeline_results["send_result"] = send_result

            # Stage 6: Memory Storage (optional)
            if store_in_memory:
                logger.info("Stage 6: Storing interaction in memory")
                interaction_data = {
                    "prospect_name": lead_data.get("name", ""),
                    "prospect_title": lead_data.get("position", ""),
                    "prospect_company": lead_data.get("company", ""),
                    "prospect_email": lead_data.get("email", ""),
                    "subject": pipeline_results["final_email"].get("subject", "") if pipeline_results["final_email"] else "",
                    "body": pipeline_results["final_email"].get("body", "") if pipeline_results["final_email"] else "",
                    "status": "sent" if pipeline_results.get("send_result", {}).get("success") else "failed",
                    "personalization_used": bool(personalization_result),
                    "optimization_used": optimize_content,
                    "pipeline_results": pipeline_results  # Store full results for learning
                }

                memory_result = self.memory_agent.store_interaction(interaction_data)
                pipeline_results["memory_stored"] = "successfully" in memory_result.lower()
                pipeline_results["memory_result"] = memory_result

        except Exception as e:
            logger.error(f"Error processing lead: {str(e)}", exc_info=True)
            pipeline_results["errors"].append(str(e))

        return pipeline_results

    def process_leads_from_csv(self,
                              csv_file_path: str,
                              name_column: str = "name",
                              company_column: str = "company",
                              email_column: str = "email",
                              linkedin_column: str = "linkedin_url",
                              position_column: str = "position",
                              optimize_content: bool = True,
                              schedule_send: bool = True,
                              store_in_memory: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple leads from a CSV file.

        Args:
            csv_file_path: Path to the CSV file
            name_column: Column name for prospect name
            company_column: Column name for company name
            email_column: Column name for email address
            linkedin_column: Column name for LinkedIn URL
            position_column: Column name for job position
            optimize_content: Whether to run content optimization
            schedule_send: Whether to schedule and send the email
            store_in_memory: Whether to store the interaction in memory

        Returns:
            List of results for each lead processed
        """
        logger.info(f"Processing leads from CSV file: {csv_file_path}")

        results = []

        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for i, row in enumerate(reader):
                    logger.info(f"Processing lead {i+1}: {row.get(name_column, 'Unknown')}")

                    # Convert row to lead data format
                    lead_data = {
                        "name": row.get(name_column, ""),
                        "company": row.get(company_column, ""),
                        "email": row.get(email_column, ""),
                        "linkedin_url": row.get(linkedin_column, ""),
                        "position": row.get(position_column, "")
                    }

                    # Skip if essential data is missing
                    if not lead_data["name"] or not lead_data["company"]:
                        logger.warning(f"Skipping lead {i+1} due to missing name or company")
                        results.append({
                            "lead_data": lead_data,
                            "error": "Missing required fields (name or company)",
                            "skipped": True
                        })
                        continue

                    # Process the lead
                    result = self.process_lead(
                        lead_data=lead_data,
                        optimize_content=optimize_content,
                        schedule_send=schedule_send,
                        store_in_memory=store_in_memory
                    )
                    results.append(result)

        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_file_path}")
            raise
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)
            raise

        logger.info(f"Finished processing {len(results)} leads from CSV")
        return results

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of all system components.

        Returns:
            Dictionary containing status information
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "memory": self.memory_agent.get_memory_summary(),
            "tools": {}
        }

        # Check agent status (basic)
        agents = {
            "research_agent": self.research_agent,
            "personalization_agent": self.personalization_agent,
            "email_writer_agent": self.email_writer_agent,
            "content_optimizer_agent": self.content_optimizer_agent,
            "scheduler_agent": self.scheduler_agent,
            "memory_agent": self.memory_agent
        }

        for name, agent in agents.items():
            status["agents"][name] = {
                "initialized": agent is not None,
                "type": type(agent).__name__
            }

        # Check tool status
        tools = {
            "email_tool": self.email_tool,
            "spam_checker": self.spam_checker,
            "linkedin_tool": self.linkedin_tool,
            "research_tool": self.research_tool
        }

        for name, tool in tools.items():
            status["tools"][name] = {
                "initialized": tool is not None,
                "type": type(tool).__name__
            }

        return status


def main():
    """Main CLI interface for the Cold Email Outreach System."""
    parser = argparse.ArgumentParser(description="AI Cold Email Outreach System")
    parser.add_argument("--mode", choices=["single", "csv", "status"], default="single",
                       help="Operation mode: single lead, CSV file, or system status")
    parser.add_argument("--name", help="Prospect name (for single mode)")
    parser.add_argument("--company", help="Prospect company (for single mode)")
    parser.add_argument("--email", help="Prospect email (for single mode)")
    parser.add_argument("--linkedin", help="Prospect LinkedIn URL (for single mode)")
    parser.add_argument("--position", help="Prospect position (for single mode)")
    parser.add_argument("--csv-file", help="Path to CSV file (for CSV mode)")
    parser.add_argument("--no-optimize", action="store_true", help="Skip content optimization")
    parser.add_argument("--no-send", action="store_true", help="Skip email sending")
    parser.add_argument("--no-memory", action="store_true", help="Skip memory storage")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize system
    system = ColdEmailSystem()

    if args.mode == "status":
        # Show system status
        status = system.get_system_status()
        print("=== Cold Email Outreach System Status ===")
        print(f"Timestamp: {status['timestamp']}")
        print("\nAgents:")
        for name, info in status["agents"].items():
            print(f"  {name}: {'✓' if info['initialized'] else '✗'} ({info['type']})")
        print("\nTools:")
        for name, info in status["tools"].items():
            print(f"  {name}: {'✓' if info['initialized'] else '✗'} ({info['type']})")
        print(f"\nMemory:\n{status['memory']}")

    elif args.mode == "single":
        # Process single lead
        if not args.name or not args.company:
            print("Error: --name and --company are required for single mode")
            sys.exit(1)

        lead_data = {
            "name": args.name,
            "company": args.company,
            "email": args.email or "",
            "linkedin_url": args.linkedin or "",
            "position": args.position or ""
        }

        print(f"Processing lead: {args.name} at {args.company}")
        result = system.process_lead(
            lead_data=lead_data,
            optimize_content=not args.no_optimize,
            schedule_send=not args.no_send,
            store_in_memory=not args.no_memory
        )

        print("\n=== Processing Results ===")
        print(f"Lead: {result['lead_data'].get('name', 'Unknown')} at {result['lead_data'].get('company', 'Unknown')}")

        # Show research summary
        if "research" in result["stages"]:
            print("\n--- Research ---")
            research = result["stages"]["research"]
            if isinstance(research, dict) and "synthesized_research" in research:
                print(research["synthesized_research"][:500] + "..." if len(research["synthesized_research"]) > 500 else research["synthesized_research"])

        # Show personalization summary
        if "personalization" in result["stages"]:
            print("\n--- Personalization ---")
            personalization = result["stages"]["personalization"]
            if isinstance(personalization, dict) and "detailed_profile" in personalization:
                print(personalization["detailed_profile"][:500] + "..." if len(personalization["detailed_profile"]) > 500 else personalization["detailed_profile"])

        # Show email
        if result["final_email"]:
            print("\n--- Generated Email ---")
            print(f"Subject: {result['final_email'].get('subject', 'No subject')}")
            print(f"\nBody:\n{result['final_email'].get('body', 'No body')}")

        # Show optimization results
        if "content_optimization" in result["stages"] and not args.no_optimize:
            print("\n--- Content Optimization ---")
            opt_result = result["stages"]["content_optimization"]
            if isinstance(opt_result, dict) and not opt_result.get("error"):
                print(f"Original Subject: {opt_result.get('original_subject', 'N/A')}")
                print(f"Optimized Subject: {opt_result.get('optimized_subject', 'N/A')}")
                print(f"Spam Score Improvement: See full results for details")

        # Show send results
        if result.get("send_result"):
            print("\n--- Email Sending ---")
            send_result = result["send_result"]
            if isinstance(send_result, dict):
                print(f"Success: {send_result.get('success', False)}")
                if send_result.get("success"):
                    print(f"Message ID: {send_result.get('message_id', 'N/A')}")
                else:
                    print(f"Error: {send_result.get('error', 'Unknown error')}")

        # Show memory storage
        print(f"\n--- Memory Storage ---")
        print(f"Stored in memory: {result.get('memory_stored', False)}")
        if result.get("memory_result"):
            print(f"Memory result: {result['memory_result']}")

        # Show errors
        if result["errors"]:
            print("\n--- Errors ---")
            for error in result["errors"]:
                print(f"  - {error}")

    elif args.mode == "csv":
        # Process leads from CSV
        if not args.csv_file:
            print("Error: --csv-file is required for CSV mode")
            sys.exit(1)

        print(f"Processing leads from CSV: {args.csv_file}")
        results = system.process_leads_from_csv(
            csv_file_path=args.csv_file,
            optimize_content=not args.no_optimize,
            schedule_send=not args.no_send,
            store_in_memory=not args.no_memory
        )

        print(f"\n=== CSV Processing Complete ===")
        print(f"Total leads processed: {len(results)}")

        successful = sum(1 for r in results if r.get("send_result", {}).get("success", False))
        failed = sum(1 for r in results if not r.get("send_result", {}).get("success", True) and not r.get("skipped", False))
        skipped = sum(1 for r in results if r.get("skipped", False))

        print(f"Successful sends: {successful}")
        print(f"Failed sends: {failed}")
        print(f"Skipped leads: {skipped}")

        # Show first few results in detail if verbose
        if args.verbose and results:
            print(f"\n--- Detailed Results (First 3) ---")
            for i, result in enumerate(results[:3]):
                print(f"\nLead {i+1}:")
                print(f"  Name: {result.get('lead_data', {}).get('name', 'Unknown')}")
                print(f"  Company: {result.get('lead_data', {}).get('company', 'Unknown')}")
                print(f"  Sent Successfully: {result.get('send_result', {}).get('success', False)}")
                if result.get("errors"):
                    print(f"  Errors: {', '.join(result['errors'])}")


if __name__ == "__main__":
    main()