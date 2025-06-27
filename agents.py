from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from langchain.chains import RetrievalQA, ConversationChain
from langchain import HuggingFaceHub
from utils.cache import get_cached_response, set_cached_response
from memory import CONV_MEMORY
from ingestion import run_full_ingest
from articles import generate_technical_article
from vectorstore import init_collections
import os

# 1. Initialize your vector store and LLM
STORE = init_collections()
llm = HuggingFaceHub(
   repo_id="tiiuae/falcon-7b-instruct",
   huggingfacehub_api_token=os.environ["HF_TOKEN"],
   model_kwargs={"temperature":0}
 )

# 2. Build the Retrieval-Augmented QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=STORE.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# 3. Wrap in a ConversationChain for short-term memory
conv_chain = ConversationChain(
    llm=llm,
    memory=CONV_MEMORY,
    verbose=False
)

def answer_question(query: str):
    """
    1) Check disk-cache for this exact query.
    2) If cached, return immediately.
    3) Otherwise run RAG → cache → return.
    Also pushes each query/answer into the conversation memory.
    """
    # 1) Cache lookup
    cached = get_cached_response(query)
    if cached:
        return cached  # (answer: str, sources: List[str])

    # 2) Retrieval + LLM
    rag_out = qa_chain({"query": query})
    answer = rag_out["result"]
    sources = [doc.page_content[:200] for doc in rag_out["source_documents"]]

    # 3) Update conversation memory
    conv_chain.predict(query=query)

    # 4) Cache full response
    set_cached_response(query, (answer, sources))
    return answer, sources

# 4. Scheduler: ingestion every 10 minutes
sched = BackgroundScheduler()
sched.add_job(
    run_full_ingest,
    "interval",
    minutes=10,
    id="ingest_job",
    replace_existing=True
)

# 5. Scheduler: daily technical-article at 23:00 UTC
sched.add_job(
    generate_technical_article,
    CronTrigger(hour=23, minute=0),
    id="daily_article",
    replace_existing=True
)

sched.start()
