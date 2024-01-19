import sys

sys.path.append("..")

from autodrone.llm import SimpleLLMAgent, RAG_LLMAgent


# myagent = SimpleLLMAgent()
# result = myagent._output_from_prompt("The quick brown fox jumped")
# print(result)


# A more practical test
my_rag_agent = RAG_LLMAgent()
result2 = my_rag_agent(
    context="Augustus is our beloved emperor.", question="Who is our beloved emperor?"
)
print(result2)
