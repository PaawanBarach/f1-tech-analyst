import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# LLM: switch to HuggingFaceHub using your HF_TOKEN env var
from langchain import HuggingFaceHub

HF_TOKEN = os.getenv("HF_TOKEN", "")
llm = HuggingFaceHub(
    repo_id="tiiuae/falcon-7b-instruct",
    huggingfacehub_api_token=HF_TOKEN,
    model_kwargs={"temperature": 0}
)

# RAG + Memory
from langchain.chains import RetrievalQA, ConversationChain
from memory import CONV_MEMORY
from vectorstore import STORE, upsert_texts
from ingestion import run_full_ingest
from articles import generate_technical_article
from utils.cache import get_cached_response, set_cached_response

# Build the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=STORE.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# Wrap in ConversationChain for short-term memory
conv_chain = ConversationChain(
    llm=llm,
    memory=CONV_MEMORY,
    verbose=False
)

def answer_question(query: str):
    # 1) Cache check
    cached = get_cached_response(query)
    if cached:
        return cached  # (answer, sources)

    # 2) RAG call
    rag_out = qa_chain({"query": query})
    answer = rag_out["result"]
    sources = [doc.page_content[:200] for doc in rag_out["source_documents"]]

    # 3) Conversation memory
    conv_chain.predict(query=query)

    # 4) Cache response
    set_cached_response(query, (answer, sources))
    return answer, sources

# Scheduler setup (only if *not* in Codespace)
if "CODESPACE_NAME" not in os.environ:
    sched = BackgroundScheduler()
    # Ingest every 10 minutes
    sched.add_job(
        run_full_ingest,
        "interval",
        minutes=10,
        id="ingest_job",
        replace_existing=True
    )
    # Daily article at 23:00 UTC
    sched.add_job(
        generate_technical_article,
        CronTrigger(hour=23, minute=0),
        id="daily_article",
        replace_existing=True
    )
    sched.start()
