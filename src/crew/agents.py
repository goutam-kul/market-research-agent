import os
from crewai import LLM, Agent
from src.config.settings import settings
from src.tools.tavily_tool import cached_tavily_search_tool
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model=settings.LLM_MODEL,
    api_key=os.getenv('GEMINI_API_KEY'),
    temperature=0.7,
)

# llm = ChatGoogleGenerativeAI(
#     model=settings.LLM_MODEL,
#     api_key=settings.GEMINI_API_KEY,
#     temperature=0.5,
#     verbose=True,
# )

researcher = Agent(
    role='Senior Industry Analyst',
    goal='Conduct thorough and comprehensive research on a given company or industry',
    backstory=(
        "You are an expert in market research with years of experience in analyzing " \
        "industry trends, company profiles, and strategic positioning. You can identify major " \
        "breakthroughs and opportunities from your research. You use web searches" \
        "to gather up-to-date information."
    ),
    verbose=True,
    llm=llm,
    tools=[cached_tavily_search_tool], 
    allow_delegation=False
)

# Agen 2: Market standard and Use case generator
use_case_generator = Agent(
    role='AI Innovation Strategist',
    goal=(
        "Identify relevant AI/ML trends in the reserached industry and generate specific, actionable " \
        "GenAI/ML use cases tailored to the target company's context and needs, following a specific detailed format."
    ),
    backstory=(
        "You are a forward thinking AI strategist with deep knowledge of Machine Learning, Large Language Models and GenAI " \
        "applications across various industries. You excel at connecting industry trends and company objectives " \
        "(like operational efficiency, customer experience) to concrete AI use cases. You are meticulous about structuring " \
        "your proposals, detailing objectives, AI application, and corss-functional benefits inspired by best practices and " \
        "real-world examples."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
    tools=[cached_tavily_search_tool]
)

# Agent 3: Resource asset collector
resource_collector = Agent(
    role='Data & Resource Scout',
    goal='Find relevant public dataset (kaggle, hugginface) and code repositories (Github) related to the proposed AI use cases.',
    backstory=(
        "You are a specialist in navigating data science platforms and code repositories." \
        "Given specific AI/ML use case, you efficiently formulate search queries to discover " \
        "relevant datasets (for training/testing) and open-source code examples (for implementation ideas) " \
        "on platform like Kaggle, Huggingface Hub, and Github. You focus on finding practical accessible resources."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
    tools=[cached_tavily_search_tool]
)

# Agent 4: Synthesizer agent
proposal_synthesizer = Agent(
    role='Senior Proposal Manager',
    goal='Consolidate research findings, prioritized use cases, and resource links into a final, well-structured, professional Markdown report.',
    backstory=(
        "You are and experienced proposal manager with a keen eye for details and clarity. " \
        "You take inputs from researchers, strategist, and resource scouts to compile comprehensive yet concise reports. " \
        "You pritoritize information based on relevance and impact, ensure professional formatting (especially markdown), " \
        "and make sure all the reference and resource links are correctly included and clickable."
    ),
    verbose=True,
    llm=llm,
    allow_delegation=False,
)