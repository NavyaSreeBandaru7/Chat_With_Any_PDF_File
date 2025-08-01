import streamlit as st
import os
import tempfile
from io import BytesIO
import time
from typing import List, Dict

# LangChain imports
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

# ============================================================================
# 🔑 ADD YOUR OPENAI API KEY HERE
# ============================================================================
# Replace 'your-openai-api-key-here' with your actual OpenAI API key
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "your-openai-api-key-here"

# Set the API key in environment
if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here":
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Page configuration
st.set_page_config(
    page_title="Chat with your PDF",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    
    .main-header {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .chat-container {
        background-color: #2d2d2d;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .upload-section {
        background-color: #2d2d2d;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .success-message {
        background-color: #28a745;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: left;
    }
    
    .ai-message {
        background-color: #495057;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
    
    .stTextInput > div > div > input {
        background-color: #3d3d3d;
        color: white;
        border: 1px solid #555;
        border-radius: 5px;
    }
    
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
    }
    
    .sample-question {
        background-color: #343a40;
        border: 1px solid #495057;
        border-radius: 5px;
        padding: 0.5rem;
        margin: 0.25rem 0;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .sample-question:hover {
        background-color: #495057;
    }
    
    .file-info {
        background-color: #17a2b8;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PDFChatBot:
    def __init__(self):
        self.vectorstore = None
        self.conversation_chain = None
        self.chat_history = []
    
    def process_pdf(self, pdf_file, openai_api_key):
        """Process uploaded PDF file"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Load PDF
            loader = PyPDFLoader(tmp_file_path)
            documents = loader.load()
            
            if not documents:
                return False, "No content found in the PDF file."
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create embeddings
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self.vectorstore = FAISS.from_documents(chunks, embeddings)
            
            # Create conversation chain
            memory = ConversationBufferMemory(
                memory_key='chat_history',
                return_messages=True,
                output_key='answer'
            )
            
            self.conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=ChatOpenAI(
                    openai_api_key=openai_api_key,
                    temperature=0,
                    model_name="gpt-3.5-turbo"
                ),
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3}),
                memory=memory,
                return_source_documents=True
            )
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return True, f"Successfully processed {len(documents)} pages from PDF!"
            
        except Exception as e:
            if 'tmp_file_path' in locals():
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
            return False, f"Error processing PDF: {str(e)}"
    
    def get_response(self, user_question):
        """Get response from the conversation chain"""
        if not self.conversation_chain:
            return "Please upload a PDF first!"
        
        try:
            response = self.conversation_chain({'question': user_question})
            return response['answer']
        except Exception as e:
            return f"Error getting response: {str(e)}"

def main():
    # Initialize session state
    if 'chat_bot' not in st.session_state:
        st.session_state.chat_bot = PDFChatBot()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = ""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📄 Chat with your PDF</h1>
        <p>Upload a PDF and start asking questions about its content!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("🔑 Configuration")
        
        # Check if API key is set in code
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here":
            openai_api_key = OPENAI_API_KEY
            st.success("✅ API Key loaded from code")
            st.info("🔒 API Key is set in the application code")
        else:
            openai_api_key = st.text_input(
                "OpenAI API Key", 
                type="password",
                help="Enter your OpenAI API key to start chatting",
                placeholder="sk-...",
                value=""
            )
            
            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
            else:
                st.warning("⚠️ Please add your API key in the code or enter it above")
        
        st.markdown("---")
        
        st.markdown("### 📋 How to Use")
        st.markdown("""
        1. **Enter API Key** above
        2. **Upload PDF** in main area
        3. **Wait** for processing
        4. **Ask questions** about your PDF
        """)
        
        st.markdown("---")
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_bot = PDFChatBot()
            st.session_state.pdf_processed = False
            st.session_state.uploaded_file_name = ""
            st.success("Chat history cleared!")
            st.rerun()
        
        # Display current status
        st.markdown("### 📊 Status")
        if st.session_state.pdf_processed:
            st.success("✅ PDF Loaded")
            st.info(f"📄 {st.session_state.uploaded_file_name}")
        else:
            st.warning("⏳ No PDF loaded")
        
        if (OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here") or openai_api_key:
            st.success("✅ API Key Set")
        else:
            st.error("❌ API Key Missing")
            st.markdown("**To add API key:**")
            st.markdown("1. Edit `app.py` file")
            st.markdown("2. Replace `your-openai-api-key-here`")
            st.markdown("3. Save and restart app")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📤 Upload PDF")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF file (max 200MB)",
            label_visibility="collapsed"
        )
        
        if uploaded_file and ((OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here") or openai_api_key):
            if not st.session_state.pdf_processed or st.session_state.uploaded_file_name != uploaded_file.name:
                with st.spinner("🧠 Processing PDF... Please wait"):
                    progress_bar = st.progress(0)
                    progress_bar.progress(25)
                    
                    # Use API key from code or input
                    api_key_to_use = OPENAI_API_KEY if (OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here") else openai_api_key
                    success, message = st.session_state.chat_bot.process_pdf(uploaded_file, api_key_to_use)
                    progress_bar.progress(100)
                    
                    if success:
                        st.success(message)
                        st.session_state.pdf_processed = True
                        st.session_state.uploaded_file_name = uploaded_file.name
                        progress_bar.empty()
                        
                        # Display file info
                        file_size = uploaded_file.size / 1024  # KB
                        st.markdown(f"""
                        <div class="file-info">
                            <strong>📄 File:</strong> {uploaded_file.name}<br>
                            <strong>📊 Size:</strong> {file_size:.1f} KB<br>
                            <strong>✅ Status:</strong> Ready for questions!
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(message)
                        progress_bar.empty()
        
        elif uploaded_file and not ((OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here") or openai_api_key):
            st.warning("⚠️ Please add your OpenAI API key!")
            st.info("💡 **Option 1:** Edit the code and add your API key at the top")
            st.info("💡 **Option 2:** Enter your API key in the sidebar")
        
        elif not uploaded_file:
            st.markdown("""
            <div class="upload-section">
                <h3>📁 Drag and drop your PDF here</h3>
                <p>Or click 'Browse files' above</p>
                <p><small>Supported: PDF files up to 200MB</small></p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💬 Chat with your PDF")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.messages:
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="user-message">
                            <strong>You:</strong> {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="ai-message">
                            <strong>AI:</strong> {message["content"]}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                if st.session_state.pdf_processed:
                    st.markdown("""
                    <div class="ai-message">
                        <strong>AI:</strong> Hello! I've analyzed your PDF. What would you like to know about it?
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 2rem; color: #888;">
                        <h3>👋 Welcome!</h3>
                        <p>Upload a PDF file to start chatting with your document.</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input area
        st.markdown("---")
        
        # Input for new question
        user_question = st.text_input(
            "Ask a question about your PDF:",
            placeholder="Type your question here...",
            key="user_input",
            disabled=not st.session_state.pdf_processed
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
        
        with col_btn1:
            send_button = st.button("📤 Send", type="primary", disabled=not st.session_state.pdf_processed)
        
        with col_btn2:
            if st.button("🔄 Refresh", disabled=not st.session_state.pdf_processed):
                st.rerun()
        
        # Process question
        if (send_button or (user_question and st.session_state.get('last_input') != user_question)) and user_question and st.session_state.pdf_processed:
            st.session_state.last_input = user_question
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_question})
            
            # Get AI response
            with st.spinner("🤔 AI is thinking..."):
                ai_response = st.session_state.chat_bot.get_response(user_question)
            
            # Add AI response
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # Clear input and rerun
            st.rerun()
        
        # Sample questions
        if st.session_state.pdf_processed and len(st.session_state.messages) == 0:
            st.markdown("### 💡 Try these sample questions:")
            
            sample_questions = [
                "What is this document about?",
                "Summarize the main points",
                "Give me the key information",
                "What are the important details?",
                "Explain the content in simple terms"
            ]
            
            for i, question in enumerate(sample_questions):
                if st.button(f"💭 {question}", key=f"sample_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": question})
                    
                    with st.spinner("🤔 AI is thinking..."):
                        ai_response = st.session_state.chat_bot.get_response(question)
                    
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p>💡 <strong>PDF Chat App</strong> | Built with Streamlit & LangChain | Powered by OpenAI</p>
        <p><small>Upload PDFs and chat with them using AI - Fast, secure, and easy to use!</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
