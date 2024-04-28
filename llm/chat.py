import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain import PromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm.document_loader import load_documents
from llm.embeddings import HuggingFaceQueryEmbeddings
from llm.llm_pipeline import create_llm_pipeline
from llm.qa_system import create_qa_system
from llm.text_processing import split_text_into_chunks
from llm.vector_stores import create_vector_store

import logging

documents = load_documents("/src/llm/csv")
texts = split_text_into_chunks(documents)

embeddings = HuggingFaceQueryEmbeddings(model_name="intfloat/multilingual-e5-large")
db = create_vector_store(texts, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

model_name = "elyza/ELYZA-japanese-Llama-2-7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(
    model_name, cache_dir="/src/llm/cache_dir"
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    torch_dtype=torch.float32,
    device_map="auto",
    cache_dir="/src/llm/cache_dir",
)
llm = create_llm_pipeline(model, tokenizer)

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = "あなたは誠実で優秀な日本人のアシスタントです。事前知識なしで以下のコンテキストを参考に200字以内で回答してください．{context}"

prompt = "{bos_token}{b_inst} {system}{prompt} {e_inst} ".format(
    bos_token=tokenizer.bos_token,
    b_inst=B_INST,
    system=f"{B_SYS}{DEFAULT_SYSTEM_PROMPT}{E_SYS}",
    prompt="{question}",
    e_inst=E_INST,
)

prompt_template = PromptTemplate(
    template=prompt,
    input_variables=["context", "question"],
)

def list_to_dict(data) -> dict:
    result = {}
    for i, value in enumerate(data):
        result[i] = value
    return result

def qa_system(text):
    _qa_system = create_qa_system(llm, retriever, prompt_template)
    result = _qa_system(text)
    message = result["result"].split("[/INST]")[-1].lstrip()
    sources = list_to_dict([source.page_content for source in result["source_documents"]])
    return message, sources
