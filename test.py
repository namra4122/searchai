def validate_query(query: str) -> str:
    """
    Validate the search query.
    
    Args:
        query (str): The search query to validate
        
    Returns:
        str: Validated query
        
    Raises:
        ValidationError: If query is invalid
    """
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")
        
    if len(query) > 500:
        raise ValidationError("Search query too long (max 500 characters)")
        
    return query.strip()

from crewai import Agent, Crew, Task, Process
from crewai_tools import SerperDevTool

search_tool = SerperDevTool(api_key="8c9fc65f81c585048a19189f0ce760b15b32c0e6")

researcher = Agent(
    role="Web Researcher",
    goal="Find accurate and relevant information from credible sources",
    backstory="You are an expert web researcher specializing in finding and analyzing information from reliable sources.",
    tools=[search_tool],
    llm="gemini/gemini-1.5-pro-latest",
    verbose=False,
    allow_delegation=False
)
            
            
# Create a search task with clear expectations
search_task = Task(
    description=f"""Use the SerperDevTool to search for: what is new happening with ai
    Instructions:
    1. Use the search tool to find relevant results
    2. For each result found, format it as follows:
       - URL on first line
       - Title on second line
       - Brief summary on following lines
    3. Separate each result with a blank line
    4. Return only the formatted results, no additional commentary""",
    expected_output="A list of search results formatted with URL, title and summary, separated by blank lines",
    agent=researcher
)


# Configure and execute the crew
crew = Crew(
    agents=[researcher],
    tasks=[search_task],
    process=Process.sequential,
    verbose=True
)

# Execute with timeout
result = crew.kickoff()
print(result)
print(crew.usage_metrics)