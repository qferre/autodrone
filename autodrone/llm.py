import nest_asyncio

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    pipeline,
)

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncChromiumLoader

from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS as Faiss

from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain_core.documents import Document

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List

from pydantic import BaseModel, PrivateAttr, computed_field


class SimpleLLMAgent:
    """
    Simple LLMAgent using HuggingFace-style code.
    """

    def __init__(self):
        print("Creating LLM Agent...")
        self.model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-v0.1",
            device_map="auto",
            # load_in_4bit=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mistral-7B-v0.1", padding_side="left"
        )
        print("LLM Agent created.")

    def _output_from_prompt(self, text: str):
        model_inputs = self.tokenizer([text], return_tensors="pt").to("cuda")
        generated_ids = self.model.generate(**model_inputs)
        output = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return output

    def process_voice_input(self, voice_input):
        """
        Taking a user voice input, returns a corresponding position.
        """
        raise NotImplementedError


# !pip install -q -U  datasets  tensorflow  playwright html2text sentence_transformers faiss-cpu
# !pip install -q  peft==0.4.0  trl==0.4.7
# !playwright install
# !playwright install-deps


class RAG_LLMAgent:
    def __init__(
        self,
        model_name="mistralai/Mistral-7B-Instruct-v0.2",
        use_4bit=True,  # Activate 4-bit precision base model loading
        bnb_4bit_compute_dtype="float16",  # Compute dtype for 4-bit base models
        bnb_4bit_quant_type="nf4",  # Quantization type (fp4 or nf4)
        use_nested_quant=False,  # Activate nested quantization for 4-bit base models (double quantization)
    ):
        # Tokenizer
        # self.model_config = transformers.AutoConfig.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        # Set up quantization config
        compute_dtype = getattr(torch, bnb_4bit_compute_dtype)
        # bnb_config = BitsAndBytesConfig(
        #     load_in_4bit=use_4bit,
        #     bnb_4bit_quant_type=bnb_4bit_quant_type,
        #     bnb_4bit_compute_dtype=compute_dtype,
        #     bnb_4bit_use_double_quant=use_nested_quant,
        # )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            # quantization_config=bnb_config,
        )

        nest_asyncio.apply()

        self.text_generation_pipeline = pipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            task="text-generation",
            temperature=0.2,
            repetition_penalty=1.1,
            return_full_text=True,
            max_new_tokens=1000,
        )

        self.retriever = None

    def __call__(self, question: str):
        mistral_llm = HuggingFacePipeline(pipeline=self.text_generation_pipeline)

        # Create prompt template from prompt template
        prompt_template = """
        ### [INST] Instruction: Answer the question based on your knowledge. If applicable, the provided context should help with the answer and should override your existing knowledge. Here is the provided context:

        {context}

        End of context.

        Output format : The output should not be wrapped in a sentence, but rather given directly. For example,
        if you are asked "Who was the first Roman Emperor ?", you should not answer "The first Roman Emperor was
        Augustus", but instead directly answer "Augustus".

        ### QUESTION:
        {question} [/INST]
        """

        # TODO : make a more suited prompt, like "here is a list of positions in format 'name \t x \t y \z' that you can use when building the trajectories, and keep The output should not be wrapped in a sentence, but rather given directly"

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=prompt_template,
        )

        # Create llm chain
        llm_chain = LLMChain(llm=mistral_llm, prompt=prompt)

        rag_chain = {
            "context": self.retriever,
            "question": RunnablePassthrough(),
        } | llm_chain

        # rag_chain.invoke("Should I start Gibbs next week for fantasy?")
        result = rag_chain.invoke(question)
        return result

    @staticmethod
    def _retrieve_urls(list_of_urls=["https://www.lipsum.com/feed/html"]):
        """Converts URL content to text document

        Args:
            list_of_urls (List[str]): List of URLS

        Returns:
            docs (List[langchain_core.documents.Document])
        """
        # Scrapes the URLs above containing the articles to index
        loader = AsyncChromiumLoader(list_of_urls)
        docs = loader.load()  # Docs is a List[Documents]

        # Converts HTML to text, and then chunk it
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)

        return docs_transformed

    @staticmethod
    def _text_to_document(text: str):
        return Document(page_content=text)

    def _create_retriever(self, list_of_urls=None, text=None):
        if list_of_urls is not None:
            docs_transformed = self._retrieve_urls(list_of_urls)
        if text is not None:
            docs_transformed = self._text_to_document(text)
        if (list_of_urls is None) and (text is None):
            raise ValueError("Need at least one of list_of_urls or text")
        if (list_of_urls is not None) and (text is not None):
            raise ValueError("Cannot specify both list_of_urls and text")

        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        chunked_documents = text_splitter.split_documents(docs_transformed)

        # Load chunked documents into the FAISS index (vectorizing them)
        db = Faiss.from_documents(
            chunked_documents,
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"),
        )
        self.retriever = db.as_retriever()
