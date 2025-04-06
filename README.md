# Market Research Agent
Multi-Agent architecture system that generates relevant AI and Generative AI (GenAI) use cases for a given Company or Industry.

## Project Pipeline and workflow  
The core idea is to built a sequential process, where a ouput of one agent goes to the next agent culminating in a comprehensive proposal. 

1. **Input**: The process starts with the user providing a target (e.g., "Tesla", "Automotive Industry", "Healthcare Insurance Providers").
2. **Agent 1: Industry/Company Research:**
   - Goal: Understand the target's context, products, focus, and key business function
   - Action: Uses web search to find the:
       - Industry/sub-sectors
       - key offerings
       - Publicly stated Strategic Focus Areas (e.g., operational efficiency, product quality, innovation - gleaned from reports, website 'About Us'/'Strategy' sections).
       - Key Business Functions/Departments: Explicitly identify relevant departments like Operations & Maintenance, Finance, Supply Chain, Quality Assurance, Production, Customer Service,             R&D, Engineering, Sales & Marketing, HR, IT, Legal, Procurement, Environmental Compliance, Executive Leadership. This list helps Agent 2 identify cross-functional benefits.
    - Output: A structured summary (internal, passed to Agent 2) containing this information. No direct user deliverable from this agent alone.
3. **Agent 2: Market Standard and Use Case generator:**
   - Goal: Identify relevant AI/ML trends and generate detailed, relevant use cases in the style of the ABC Steel PDF.
   - Action:
       - Take the reserach summary from Agent 1.
       - Uses web search (Tavily) for industry trends ("AI in steel manufacturing", "GenAI for industrial processes", "McKinsey digital transformation metals") and competitor activities.
       - Generate Use cases:
           - Use Case title
           - Objective/use case
           - AI application
           - Cross-functional benefits
           - Reference/Inspiration: (e.g., "Source: Analysis of industry best practices", "Source: Competitor X implementation news article [URL]", "Source: Deloitte AI Trends Report        
             [URL/Name]")
    - Output: A structured list of potential use cases with all the fields mentioned above. This output is passed to Agent 3.        
4. **Agent 3**: Resource  asset collector
  - Goal: Find relevant datasets and code resources for the generated use cases, presenting links like the CSV example.
  - Action:
      - Takes the list of usecases from Agent 2:
      - For each Use Case Title and AI application description:
          - Formulates search queries for Kaggle, HuggingFace, GitHub (e.g., "predictive maintenance dataset kaggle", "steel defect detection computer vision github", "demand forecasting                 supply chain huggingface dataset").
          - Uses a search tool (Tavily, potentially prompted to focus on these sites) to find relevant links.
          - Collects multiple relevant URLs per use case where possible.
  - Output: An updated list of use cases, where each use case now also includes a Resource Links section containing the raw URLs found, potentially separated by newlines (similar to the CSV example's multiline cell content).
5. **Agent 4**: Final Proposal Synthesizer:
    - Goal: Consolidate, prioritize, and format the final output into a professional report, combining the detailed use cases with clickable resource links.
    - Action:
        - Takes the enriched use case list from Agent 3 and the context summary from Agent 1.
        - Reviews and prioritizes the use cases (e.g., select Top 5-10 based on relevance, potential impact).
        - Formats the final report in Markdown.
        - Structure:
            - Introduction: Brief summary of the company/industry context (from Agent 1).
            - Recommended Use Cases Section:
                - For each prioritized use case:
                    - Present Use Case Title, Objective/Use Case, AI Application, Cross-Functional Benefit (formatted cleanly, perhaps using bullet points under each department like the
                      PDF).
                    - Include the Reference/Inspiration: source.
                    - Add a Potential Resources: section. List the resource URLs collected by Agent 3, formatted as clickable Markdown links. Example:
                  ```markdown
                    **Potential Resources:**
                    *   [Predictive Maintenance Classification Dataset](URL_KAGGLE_1) on Kaggle
                    *   [LSTM Predictive Maintenance Code](URL_KAGGLE_2) on Kaggle
                    *   [Predictive Maintenance Dataset Ai4i 2020](URL_KAGGLE_3) on Kaggle
                    *   [ML Predictive Maintenance Repo](URL_GITHUB_1) on GitHub
                    ```
    - Output: A single, well-formatted Markdown file containing the final proposal.

