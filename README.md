# OLLAMA Setup

## Downloading OLLAMA

To start using OLLAMA, we need to download the OLLAMA model.

You can download the OLLAMA model by clicking on this [link](https://ollama.com/download) and following the instructions. Once downloaded, you'll have access to a vast library of models for various applications.

## Running OLLAMA

Once you've downloaded the OLLAMA model, we can run it using the `ollama serve` command.

To start the server at localhost:11434, simply run:
```
ollama serve
```

This will launch the OLLAMA server. You can access it from your web browser by navigating to [http://localhost:11434](http://localhost:11434).

## Verifying the Connection

To verify that you've successfully connected to OLLAMA, simply open a new tab in your web browser and navigate to `http://localhost:11434`.

If everything is working properly, you should see a chat interface where you can interact with the OLLAMA model. If you encounter any issues or have questions, feel free to ask!

## Running Your Python Application

Now that we've set up OLLAMA and verified our connection, it's time to run your Python application.

First, make sure you have Python 3.12 installed on your system.

Next, create a new virtual environment using the following command:
```
python3.12 -m venv .py312
```

This will create a new virtual environment named `.py312` within the current directory.

Source the virtual environment by running:
```bash
source .py312/bin/activate
```

Once activated, you can install any required dependencies using pip:
```bash
pip install -r requirements.txt
```

Finally, run your Python application using:
```
python assistant.py
```

On line 73 of `assistant.py`, the AI Friend object is created with the input file name provided by the user. This allows for easy integration of your own PDF files into the conversation.

Only Pdf name: for FinancialManagement.pdf file -> only write Assistant("FinancialManagement")

### Linux (Ubuntu/Debian-based systems)

For Linux systems, the commands may be slightly different. Here are some examples:

*   Create a new virtual environment:
```bash
python3.12 -m venv .py312
```
*   Activate the virtual environment:
```
source .py312/bin/activate
```
*   Install dependencies using pip:
```bash
pip install -r requirements.txt
```

### macOS (using Homebrew)

For systems based on macOS, you can use the following commands:

*   Create a new virtual environment:
```bash
python3.12 -m venv .py312
```
*   Activate the virtual environment:
 ```
source .py312/bin/activate
```

*   Install dependencies using pip:
```
pip install -r requirements.txt
```

### macOS (using Homebrew and Xcode)

If you're running on a system with an x86_64 architecture, you may need to use `gcc` instead of `g++` when compiling your code. Here's how:

*   Create a new virtual environment:
```bash
python3.12 -m venv .py312
```
*   Activate the virtual environment:
```
source .py312/bin/activate
```

*   Install dependencies using pip and `gcc` (or `g++`):
```
pip install -r requirements.txt
python assistant.py 
```
