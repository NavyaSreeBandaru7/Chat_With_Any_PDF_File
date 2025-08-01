# Chat_With_Any_PDF_File
# 🚀 Quick Setup Guide - PDF Chat App

## Step 1: Get Your OpenAI API Key

1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Click on "API Keys" in the left sidebar
4. Click "Create new secret key"
5. Copy the key (it starts with `sk-`)

## Step 2: Add API Key to Code

1. Open the `app.py` file in any text editor
2. Find this line near the top (around line 20):

```python
OPENAI_API_KEY = "your-openai-api-key-here"
```

3. Replace `your-openai-api-key-here` with your actual API key:

```python
OPENAI_API_KEY = "sk-proj-your-actual-key-here"
```

**Example:**
```python
# Before:
OPENAI_API_KEY = "your-openai-api-key-here"

# After:
OPENAI_API_KEY = "your_openai_api_key"
```

4. Save the file

## Step 3: Install Dependencies

Open terminal/command prompt and run:

```bash
pip install streamlit langchain openai faiss-cpu PyPDF2 python-dotenv tiktoken
```

## Step 4: Run the Application

```bash
streamlit run app.py
```

## Step 5: Use the App

1. The app will open in your browser at `http://localhost:8501`
2. You'll see "✅ API Key loaded from code" in the sidebar
3. Upload a PDF file
4. Wait for processing (30-60 seconds)
5. Start asking questions!

## 🎉 That's it!

Your PDF chat app is now ready to use with your API key built right into the code!

## 🔒 Security Note

- Never share your `app.py` file with others after adding your API key
- Keep your API key private and secure
- Consider using environment variables in production

## 💡 Tips

- Start with small PDF files (under 5MB) for faster processing
- Ask specific questions for better answers
- Use the sample questions to get started quickly

---

**Enjoy chatting with your PDFs!** 📄💬
