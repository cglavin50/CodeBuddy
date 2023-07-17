from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from git import Repo
import os
from dotenv import load_dotenv

install_path = "./codebase/"
load_dotenv('./env', verbose=True)

# clone the repository (go-libp2p)
repo = Repo.clone_from(
    "https://github.com/libp2p/go-libp2p",
    to_path = install_path
)

# load source code into one large document
loader = GenericLoader.from_filesystem(
    path = install_path,
    glob="**/*",
    suffixes=[".go"],
    parser=LanguageParser(language=Language.GO, parser_threshold=500),
)
documents = loader.load()

# split the document
go_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.GO, chunk_size=2000, chunk_overlap=200
)
texts = go_splitter.split_documents(documents)

# create and save embeddings
embeddings = OpenAIEmbeddings(disallowed_special=(), openai_api_key=os.environ["OPENAI_API_KEY"]) # required to set this disallowed_special to avoid errors from underlying tiktoken module use
db = Chroma.from_documents(texts, embeddings)

# create a retriever function
retriever = db.as_retriever(
    search_type="mmr", # experiment and research similarity as well
    search_kwargs={"k": 8}, # research this
)

llm = ChatOpenAI(temperature=0.1, openai_api_key=os.environ["OPENAI_API_KEY"])
qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)
chat_history = []

# now ask question, and append to chat history