from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.vectorstores.redis import Redis
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.retrievers import SVMRetriever
from git import Repo
import os
from dotenv import load_dotenv
import time

start = time.time()
load_dotenv('./.env', verbose=True)
install_path = "./codebase/"

# clone the repository (go-libp2p)
# repo = Repo.clone_from(
#     "https://github.com/libp2p/go-libp2p",
#     to_path = install_path
# )

# load source code into one large document
loader = GenericLoader.from_filesystem(
    path = install_path,
    glob="**/*",
    suffixes=[".go"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
) # only supports python and JS for now, however the recursive text splitter is what does the work anyways so should be okay
documents = loader.load()

# split the document
go_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.GO, chunk_size=2000, chunk_overlap=200
)
texts = go_splitter.split_documents(documents)

# create and save embeddings
embeddings = OpenAIEmbeddings(disallowed_special=(), openai_api_key=os.environ["OPENAI_API_KEY"]) # required to set this disallowed_special to avoid errors from underlying tiktoken module use
db = Chroma.from_documents(texts, embeddings)
rds = Redis.from_documents(texts, embeddings, redis_url="redis://localhost:6379", index_name="libp2p") # this should create the index "libp2p", using the texts and embedding model passed in


# create a retriever function
retriever = db.as_retriever(
    search_type="similarity", # experiment and research similarity as well, so far better results with mmr
    search_kwargs={"k": 8}, # research this
)
rds_retriever = rds.as_retriever(
    search_type="similarity", # experiment and research similarity as well, so far better results with mmr
    search_kwargs={"k": 8}, # research this
)
#svm_retriever = SVMRetriever.from_documents(texts, embeddings)

llm = ChatOpenAI(temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"])
qa1 = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)
#qa2 = ConversationalRetrievalChain.from_llm(llm, retriever=svm_retriever)
qa3 = ConversationalRetrievalChain.from_llm(llm, retriever=rds_retriever)
chat_history = []
memory = ConversationBufferMemory(memory_key = "chat_history", retriever=retriever)

# now ask question, and append to chat history
question = "Can you show me how to automatically find and connect to relays via the autorelay module?"
result1 = qa1({"question": question, "chat_history": chat_history})
# result2 = qa2({"question": question, "chat_history": chat_history})
result3 = qa3({"question": question, "chat_history": chat_history})
chat_history.append((question, result1['answer'])) # append to this as we go
#print("MMR search")
#print(result1['answer'])
#print("SVM answer")
#print(result2['answer'])

file = open("example-auto-relay-chroma-mmr.md", 'w')
count = file.write(result1['answer'])
file.close()
file = open("example-auto-relay-rds-sim.md", 'w')
count = file.write(result3['answer'])
file.close()

print("Finished in", time.time() - start, "seconds")