from langchain.chains import RetrievalQA


def create_qa_system(llm, retriever, prompt_template):
    result = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template},
        verbose=False,
        return_source_documents=True,
    )
    return result
