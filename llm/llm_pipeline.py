from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import pipeline


def create_llm_pipeline(model, tokenizer):
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
    )
    return HuggingFacePipeline(pipeline=pipe)
