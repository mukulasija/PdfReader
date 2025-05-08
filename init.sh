download ollama https://ollama.com/download
run ollama serve
it will start the ollama server at localhost:11434
check and verify it on your browser with localhost:11434
once verified

run this command on your terminal
ollama run llama3.2:1b
it will start download llama3.2 binary files from ollama server, let it download
once downloaded it will allow you to chat in that terminal with llama3.2:1b model

now ollama is setup, we will run our python application

install python3.12.3
then run
python3.12 -m .venv .py312
source .py312/bin/activate
this will create a virtual enviornment

pip install -r requirements.txt
python assistant.py

on line number 73 or assistant.py
ai_friend = Assistant("FinancialManagement")
it takes an input of pdf file name
so you can give your own pdf name
and thats all, you can chat with llm