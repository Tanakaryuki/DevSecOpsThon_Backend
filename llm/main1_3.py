import torch
from langchain import PromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer

from document_loader import load_documents
from embeddings import HuggingFaceQueryEmbeddings
from llm_pipeline import create_llm_pipeline
from qa_system import create_qa_system
from text_processing import split_text_into_chunks
from vector_stores import create_vector_store

documents = load_documents("/workspace/csv")
texts = split_text_into_chunks(documents)

embeddings = HuggingFaceQueryEmbeddings(model_name="intfloat/multilingual-e5-large")
db = create_vector_store(texts, embeddings)
retriever = db.as_retriever(search_kwargs={"k": 3})

model_name = "elyza/ELYZA-japanese-Llama-2-7b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir="/workspace/cache_dir")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    torch_dtype=torch.float32,
    device_map="auto",
    cache_dir="/workspace/cache_dir",
)
llm = create_llm_pipeline(model, tokenizer)

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
DEFAULT_SYSTEM_PROMPT = "あなたは誠実で優秀な日本人のアシスタントです。事前知識なしで以下のコンテキストを参考に回答してください．{context}"

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
qa_system = create_qa_system(llm, retriever, prompt_template)

while True:
    user_input = input("質問を入力してください (終了する場合は 'exit' を入力): ")
    if user_input.lower() == "exit":
        print("終了します。")
        break
    result = qa_system(user_input)
    answer = result["result"].split("[/INST]")[-1].lstrip()
    source = result["source_documents"]
    print("回答")
    print(answer)
    print("-------------------")
    print("資料")
    print(source)
