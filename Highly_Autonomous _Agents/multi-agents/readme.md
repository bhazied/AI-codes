```bash
# 1. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 2. Install all required libraries
pip install -r requirements.txt

# 3. Export your OpenAI API Key and if you dont need it use the openai:o4-mini model 
export OPENAI_API_KEY="your-actual-openai-api-key"
# On Windows Command Prompt: set OPENAI_API_KEY="your-actual-openai-api-key"
# On Windows PowerShell: $env:OPENAI_API_KEY="your-actual-openai-api-key"
```
