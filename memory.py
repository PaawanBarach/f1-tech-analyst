from langchain.memory import ConversationBufferMemory

# Keeps the last N exchanges in RAM
CONV_MEMORY = ConversationBufferMemory(
    memory_key="chat_history",
    input_key="query",
    output_key="result",
    k=20  # number of turns to remember
)
