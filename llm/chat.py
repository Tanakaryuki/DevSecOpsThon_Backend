import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from llm.document_loader import load_documents
from llm.embeddings import HuggingFaceQueryEmbeddings
from llm.llm_pipeline import create_llm_pipeline
from llm.text_processing import split_text_into_chunks
from llm.vector_stores import create_vector_store

import logging


documents = load_documents("/src/llm/csv")
texts = split_text_into_chunks(documents)

embeddings = HuggingFaceQueryEmbeddings(model_name="intfloat/multilingual-e5-large")
db = create_vector_store(texts, embeddings)

model_name = "elyza/ELYZA-japanese-Llama-2-7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(
    model_name, cache_dir="/src/llm/cache_dir", use_fast=False
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    torch_dtype=torch.float32,
    device_map="auto",
    cache_dir="/src/llm/cache_dir",
)

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = "あなたは誠実で優秀な日本人のアシスタントです。事前知識なしで以下のコンテキストを参考に200字以内で回答してください．"


def list_to_string(data) -> dict:
    strings = []
    for value in data:
        strings.append(value)
    return ','.join(strings)

def get_context(search_text, db):
    context = list_to_string([source.page_content for source in db.search(search_text, "similarity")])
    return context

def list_to_dict(data) -> dict:
    result = {}
    for i, value in enumerate(data):
        result[i] = value
    return result

async def qa_system(text, max_length=128, k=3):
    import re
    context = get_context(text, db)
    prompt = f"{tokenizer.bos_token}{B_INST} {B_SYS}{DEFAULT_SYSTEM_PROMPT}{context}{E_SYS}{text} {E_INST} "
    with torch.no_grad():
        token_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
        eos_token_id = tokenizer.eos_token_id
        pattern = r"<0x[0-9A-Fa-f]+>"
        buffer = ""
        for _ in range(max_length):
            logits = model(token_ids).logits[:, -1, :]
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            new_token_id = torch.multinomial(probabilities, 1).item()
            if new_token_id == eos_token_id:
                break
            new_token_str = tokenizer.decode(new_token_id, skip_special_tokens=True)
            if re.match(pattern, new_token_str):
                buffer += new_token_str
            elif buffer != "":
                try:
                    byte_data = bytes.fromhex(buffer.replace("<0x", "").replace(">", "")).decode('utf-8')
                except:
                    byte_data = buffer.replace("<0x", "").replace(">", "")
                logging.error(byte_data)
                yield byte_data
                buffer = ""
            else:
                logging.error(new_token_str)
                yield new_token_str
            token_ids = torch.cat([token_ids, torch.tensor([[new_token_id]]).to(token_ids.device)], dim=-1)
