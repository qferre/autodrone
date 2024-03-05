import sys

sys.path.append("..")  # If called from tests directory
sys.path.append(".")  # If called from main directory

from autodrone.llm import RAG_LLMAgent

# Simple test

my_rag_agent = RAG_LLMAgent(
    # model_name="mistralai/Mistral-7B-Instruct-v0.2",
    model_name="microsoft/phi-2",  # Try a smaller model, TODO make it default if it works well
)

my_rag_agent.setup_retriever_for_this_context(text="Augustus is our beloved emperor.")

result = my_rag_agent(
    question="Who is our beloved emperor?",
)
print(result)
assert result == "Augustus"


# Drone test
my_rag_agent = RAG_LLMAgent(
    model_name="mistralai/Mistral-7B-Instruct-v0.2", prompt_template_key="drone_loc"
)

index = """
Alice's desk\t10\t10\t0
Guillaume's desk\t0\t0\t0
"""
my_rag_agent.setup_retriever_for_this_context(text=index)

result = my_rag_agent(
    question="Give me the coordinates of the midpoint between Alice's and Guillaume's desk.",
)
print(result)
assert result == "(5, 5, 0)"
