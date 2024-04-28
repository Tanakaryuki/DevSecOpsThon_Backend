from glob import glob

from langchain_community.document_loaders import TextLoader


def load_documents(directory):
    all_documents = []
    for csv_dir in glob(directory):
        for sub_dir_path in glob(f"{csv_dir}/*"):
            loader = TextLoader(sub_dir_path)
            documents = loader.load()
            all_documents.extend(documents)
    return all_documents
