from crewai import Task
from crew.agents import researcher, use_case_generator, resource_collector, proposal_synthesizer

research_task = Task(
    description=(
        "Conduct thorough research on the company: '{company_name}' or the industry:  '{industry_name}'. " \
        "Identify its specific industry sector (e.g., Steel Manufacturing, SBQ steel production)." \
        "Key produce/service offerings (e.g., Special )" \
        "Publicly stated strategic focus areas (e.g., Operational efficiency, Product Quality Enhancement, Sustainability" \
        "found on their website or reports), and identify the main business functions/departments involved" \
        "(e.g., Operations, Maintenance, Finance, Supply Chain, Quality Assurance, Production, Customer service, R&D, HR" \
        "IT, Legal, Sales, Marketing." \
        "Compile these findings in a structured summary document."
    ),
    expected_output=(
        "A structued text summary containing clearly defined sections for:\n" \
        "- Target: [Company name or Industry name provided]\n" \
        "- Industry & Sector: [Specific Industry and Sector identified]\n" \
        "- Key Offerings: [List of primary products/services]\n" \
        "- Strategic Focus Area:  [Bulleted list of identified goals/priorities]\n" \
        "- key Business Functions/Departments: [List of relevant departmens]"
    ), 
    agent=researcher
)

# Task 2: Use case generator task
use_case_generation_task = Task(
    description=(
        "Based on the research summary provided (context), identify current AI ML, and GenAI trends within the company's " \
        "specific industry sector. Use web serach  if needed for lastest trends or competitor activities. " \
        "The, generate 5-10 relevant and creative AI/ML/GenAI use cases tailored to '{company_name}' (or the industry '{industry_name}'). " \
        "Focus on leveraging AI to address their strategic focus areas (e.g., improving operations, quality, customer experience). " \
        "For each use case, structure the output *exactly* as follows:\n" \
        "Use case title: [Clear Title]\n" \
        "Objective/Use Case: [Detailed objective]\n" \
        "AI Application: [Specific AI/ML technique (e.g., Predictive Maintenance using ML, Defect Detection using CV, Document Analysis using LLM)]\n" \
        "Cross-Functional Benefit:\n"
        "   - [Department 1 from Research]: [Benefit]\n" \
        "   - [Department 2 from Research]: [Benefit]\n"
        "   - [... as applicable]\n" \
        "Reference/Inspiration: [Source of idea - e.g., 'Industry best practice', 'Competitor X example [URL]', 'Consulting Report [Name/URL]']"
    ),
    expected_output=(
        "A list of 5-10 detailed use cases formatted precisely as specified in the description, " \
        "drawing direct connection between  the AI application and the company's context/goals from the reserach summary. " \
        "Ensure the cross-functional benefits list relevant departments identified in the reserach."
    ),
    agent=use_case_generator,
    context=[research_task]  # This tasks depends on the output from the research_task
)

# Task 3: Collect Resource task 
resource_collection_task = Task(
    description=(
        "For each AI/ML use cased provided (context), identify the 'Use Case Title' and 'AI application'. " \
        "Formulate specific search queries to find relevant resources on Kaggle, HuggingFace Hub, and Github. " \
        "Search for potential datasets (e.g., 'predictive maintainence dataset kaggle', 'steel defect image huggingface') " \
        "and relevant code repositories (e.g., 'demand forcasting python github', 'llm document summarization implementation'). " \
        "collect 3-5 relevant resource URLs for each use case where possible."
    ),
    expected_output=(
        "An updated version of the use case list, where each use case now includes an additional section:\n" \
        "Potential Resources:\n" \
        "- [URLS 1]\n" \
        "- [URLS 2]\n" \
        "- [...]\n" \
        "If no relevant resources are found for a specific use case after searching, state 'No Specific public resources readil found'."
    ),
    agent=resource_collector,
    context=[use_case_generation_task] # Depends on Task 2 
)

# Task 4: Proposal synthesizer 
proposal_synthesis_task = Task(
    description=(
        "Review the initial research summary and add the list of use cases with resource links (context). " \
        "Select the top 7-10 most impactful and relevant use cases for '{company_name}' (or the industry '{industry_name}')," \
        "considering their strategic focus and potential feasibility. " \
        "Compile a final proposal report in Markdown format. The report should include:\n" \
        "1. A brief  introduction summarizing the company/industry context based on the initial research.\n" \
        "2. A section titled 'Recommended AI/ML Use Cases'.\n" \
        "3. For each selected use case, present all the details (Title, Objective, AI Application, Cross-Functional Benefits, Reference/Inspiration) clearly formatted.\n" \
        "4. Under each use case, add a 'Potential Resources' subsection listing the collected URL)." \
        # "Try to infer a sensible Link Text (e.g., 'Kaggle Dataset', 'Github Repo', 'HugginFace Model').\n" \
        "Ensure the final output is clean, professional, and ready for presentation."
    ),
    expected_output=(
        "A single well-formatted Markdown string containing the complete final proposal. " \
        "The report must include in introduction, the prioritized list of use cases with all the details, " \
        "and clickable Markdown links for the collected resources."
    ),
    agent=proposal_synthesizer,
    context=[resource_collection_task]
)