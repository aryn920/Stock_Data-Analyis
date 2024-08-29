import os
import streamlit as st
import pickle
import time
import langchain
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

st.title("News Research Tool 🗞️📈")
st.sidebar.title('News Article URLs')

urls=[]
for i in range(4):
    url = st.sidebar.text_input(f"URL{i+1}")
    urls.append(url)

process_url_clicked = st.sidebar.button("Process for Insight")

file_path= "faiss_store_openai.pkl"
main_placeholder = st.empty()
llm = OpenAI(temperature = 0.9, max_tokens = 500)

if process_url_clicked:
    # loading the data
    loader = UnstructuredURLLoader(urls = urls)
    main_placeholder.text("Data Loading Initiated 🧑🏽‍💻🏽‍💻")
    data = loader.load()

    #splitting the data
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n','\n','.',','],
        chunk_size=1000
    )
    main_placeholder.text("Text Splitting has Started 📑")
    docs = text_splitter.split_documents(data)

    #create embeddings
    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)
    main_placeholder.text("Embedding Vector Started Building 🧑🏽‍💻🏽‍💻")
    time.sleep(2)

    #save the FAISS index to a pickle file
    with open (file_path,"wb") as f:
        pickle.dump(vectorstore_openai,f)

query = main_placeholder.text_input("What can I help you with today? ")
if query:
    if os.path.exists(file_path):
        with open(file_path,"rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever = vectorstore.as_retriever())
            result = chain({"question": query}, return_only_outputs = True)
            st.header("Answer")
            st.subheader(result['answer'])