from crew.crew import market_research_crew
from loguru import logger

inputs = {
    'company_name': 'Tesla Motors',
    'industry_name': 'Electric Vehicle'
}


if __name__ == "__main__":
    logger.info("🚀 Starting Market Research & Use Case Generation Crew...")
    # Kick off the crew
    try:
        result = market_research_crew.kickoff(inputs=inputs)
        logger.info("\n\n✅ Crew execution finished successfully!")
        logger.info("📝 Final Proposal:\n")
        print(result)

        # Optional: Save result to a markdown file
        result_str = str(result)
        output_filename = f"proposal_{inputs.get('company_name') or inputs.get('industry_name', 'output').replace(' ', '_')}.md"
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(result_str)
        print(f"\n📄 Report saved to: {output_filename}")

    except Exception as e:
        logger.error(f"\n\n❌ An error occurred during crew execution: {e}")