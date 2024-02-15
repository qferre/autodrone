import sys

sys.path.append("..")  # If called from tests directory
sys.path.append(".")  # If called from main directory

from autodrone.llm import RAG_LLMAgent


my_rag_agent = RAG_LLMAgent(
    model_name="microsoft/phi-2",  # Try a smaller model, TODO make it default if it works well
)

# Set context
my_rag_agent._create_retriever(text="Augustus is our beloved emperor.")

result = my_rag_agent(
    question="Who is our beloved emperor?",
)
print(result)
assert result == "Augustus."
