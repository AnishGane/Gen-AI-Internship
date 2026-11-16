import streamlit as st
from Week8.config import Settings
from Week8.core.documents import parse_uploads
from Week8.core.pipeline import RAGPipeline

@st.cache_resource(show_spinner=False)
def get_pipeline(api_key: str, index_path: str, embedding_model: str, chat_model: str):
    settings = Settings(
        api_key=api_key,
        index_path=index_path,
        embedding_model=embedding_model,
        chat_model=chat_model,
    )
    return RAGPipeline(settings)

def main() -> None:
    st.set_page_config(page_title="Document Q&A | RAG", page_icon="📚", layout="wide")
    st.title("📚 Ask your documents")
    st.write("Upload documents, index their meaning with embeddings, and ask questions with cited answers.")

    with st.sidebar:
        st.header("Settings")
        configured_key = Settings.api_key
        try:
            configured_key = st.secrets.get("OPENROUTER_API_KEY", configured_key)
        except Exception:
            pass
        api_key = st.text_input(
            "OpenRouter API key", value=configured_key, type="password",
            help="Used for free-model answer generation. It is not saved by this app.",
        )
        embedding_model = st.text_input("Local embedding model", value="sentence-transformers/all-MiniLM-L6-v2")
        chat_model = st.text_input("OpenRouter chat model", value="openrouter/free", help="Use openrouter/free or a model ID ending in :free.")
        index_path = st.text_input("Local vector index", value=".rag_index")
        st.caption("The local ChromaDB index persists between runs. Avoid indexing sensitive material on shared devices.")

    if not api_key:
        st.info("Add an OpenRouter API key in the sidebar to enable answers. Embeddings run locally for free.")
        st.stop()

    pipeline = get_pipeline(api_key, index_path, embedding_model, chat_model)
    st.subheader("1. Add documents")
    uploads = st.file_uploader(
        "Choose PDF, TXT, or Markdown files", type=["pdf", "txt", "md"], accept_multiple_files=True
    )
    if st.button("Index documents", type="primary", disabled=not uploads):
        try:
            with st.spinner("Reading, chunking, and embedding documents…"):
                documents, warnings = parse_uploads(uploads)
                for warning in warnings:
                    st.warning(warning)
                if documents:
                    count = pipeline.index_documents(documents)
                    st.success(f"Indexed {count} text chunks from {len(documents)} document(s).")
                    st.sidebar.caption(f"Indexed chunks: {pipeline.store.collection.count()}")
                else:
                    st.error("No readable document text was found. Check the file contents and try again.")
        except Exception as exc:
            st.error(f"Indexing failed: {exc}")

    st.subheader("2. Ask a question")
    question = st.text_input("Question", placeholder="What does the document say about…?")
    if st.button("Get answer", disabled=not question.strip()):
        try:
            with st.spinner("Searching the vector index and preparing an answer…"):
                result = pipeline.ask(question)
            if not result.sources:
                st.warning(result.answer)
            else:
                st.markdown(result.answer)
                st.markdown("#### Sources")
                for source in result.sources:
                    with st.expander(f"[{source['id']}] {source['filename']} · chunk {source['chunk_index']}"):
                        st.write(source["text"])
        except Exception as exc:
            st.error(f"Question failed: {exc}")

if __name__ == "__main__":
    main()