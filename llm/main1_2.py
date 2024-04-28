from document_loader import load_documents
from embeddings import HuggingFaceQueryEmbeddings
from text_processing import split_text_into_chunks
from vector_stores import create_vector_store

documents = load_documents("/workspace/csv")
texts = split_text_into_chunks(documents)

embeddings = HuggingFaceQueryEmbeddings(model_name="intfloat/multilingual-e5-large")
db = create_vector_store(texts, embeddings)

print("データ")
print("-------------")
print(texts[:10])
print("-------------")
print("ベクトル検索「アコーディオン」で検索")
search_text = "アコーディオン"
print(db.search(search_text, "similarity"))
