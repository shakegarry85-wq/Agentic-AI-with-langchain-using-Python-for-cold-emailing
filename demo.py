"""
Demo script showing how to use the Cold Email Outreach System.
"""

from main import ColdEmailSystem

def demo_single_lead():
    """Demonstrate processing a single lead."""
    print("=== Cold Email Outreach System Demo ===\n")

    # Initialize the system
    system = ColdEmailSystem()

    # Define a sample lead
    lead_data = {
        "name": "John Doe",
        "company": "Acme Corp",
        "email": "john.doe@acmecorp.com",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "position": "VP of Engineering"
    }

    print(f"Processing lead: {lead_data['name']} at {lead_data['company']}")
    print("-" * 50)

    # Process the lead through the full pipeline
    result = system.process_lead(
        lead_data=lead_data,
        optimize_content=True,
        schedule_send=True,  # This will attempt to send (will fail without real SMTP config)
        store_in_memory=True
    )

    # Display results
    print("\n=== RESULTS ===\n")

    # Research summary
    if "research" in result["stages"]:
        research = result["stages"]["research"]
        if isinstance(research, dict) and "synthesized_research" in research:
            print("RESEARCH INSIGHTS:")
            print(research["synthesized_research"][:300] + ("..." if len(research["synthesized_research"]) > 300 else ""))
            print()

    # Personalization summary
    if "personalization" in result["stages"]:
        personalization = result["stages"]["personalization"]
        if isinstance(personalization, dict) and "detailed_profile" in personalization:
            print("PROSPECT PROFILE:")
            print(personalization["detailed_profile"][:300] + ("..." if len(personalization["detailed_profile"]) > 300 else ""))
            print()

    # Generated email
    if result["final_email"]:
        print("GENERATED EMAIL:")
        print(f"Subject: {result['final_email'].get('subject', 'No subject')}")
        print()
        print("Body:")
        print(result['final_email'].get('body', 'No body'))
        print()

    # Optimization results
    if "content_optimization" in result["stages"]:
        opt_result = result["stages"]["content_optimization"]
        if isinstance(opt_result, dict) and not opt_result.get("error"):
            print("CONTENT OPTIMIZATION:")
            print(f"Original Subject: {opt_result.get('original_subject', 'N/A')}")
            print(f"Optimized Subject: {opt_result.get('optimized_subject', 'N/A')}")
            print()

    # Send results
    if result.get("send_result"):
        print("EMAIL SENDING:")
        send_result = result["send_result"]
        if isinstance(send_result, dict):
            print(f"Success: {send_result.get('success', False)}")
            if send_result.get("success"):
                print(f"Message ID: {send_result.get('message_id', 'N/A')}")
            else:
                print(f"Error: {send_result.get('error', 'Unknown error')} (Expected without SMTP config)")
        print()

    # Memory storage
    print(f"MEMORY STORAGE: {'Success' if result.get('memory_stored') else 'Failed'}")
    if result.get("memory_result"):
        print(f"Memory result: {result['memory_result']}")

    # Errors
    if result["errors"]:
        print("\nERRORS ENCOUNTERED:")
        for error in result["errors"]:
            print(f"  - {error}")

def demo_csv_processing():
    """Demonstrate processing leads from CSV file."""
    print("\n=== CSV PROCESSING DEMO ===\n")

    # Initialize the system
    system = ColdEmailSystem()

    # Process leads from CSV (without sending to avoid errors)
    try:
        results = system.process_leads_from_csv(
            csv_file_path="example_leads.csv",
            optimize_content=True,
            schedule_send=False,  # Set to False to avoid sending attempts
            store_in_memory=True
        )

        print(f"Processed {len(results)} leads from CSV file")

        # Summary statistics
        processed_with_email = sum(1 for r in results if r.get("final_email"))
        stored_in_memory = sum(1 for r in results if r.get("memory_stored"))

        print(f"Leads with generated emails: {processed_with_email}")
        print(f"Leads stored in memory: {stored_in_memory}")

        # Show first result as example
        if results:
            print("\n--- Example Result (First Lead) ---")
            first_result = results[0]
            print(f"Name: {first_result.get('lead_data', {}).get('name', 'Unknown')}")
            print(f"Company: {first_result.get('lead_data', {}).get('company', 'Unknown')}")

            if first_result.get("final_email"):
                email = first_result["final_email"]
                print(f"Subject: {email.get('subject', 'No subject')}")
                print(f"Body preview: {email.get('body', 'No body')[:100]}...")

    except FileNotFoundError:
        print("CSV file not found. Please run the setup first to generate example_leads.csv")
    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    # Run single lead demo
    demo_single_lead()

    # Run CSV demo
    demo_csv_processing()

    print("\n=== Demo Complete ===")
    print("Check the logs file (cold_email_system.log) for detailed execution logs.")
    print("To actually send emails, configure SMTP credentials in .env file.")