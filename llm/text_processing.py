from langchain.text_splitter import CharacterTextSplitter


def split_text_into_chunks(documents):
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=512,
        chunk_overlap=20,
    )
    return text_splitter.split_documents(documents)
