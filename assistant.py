from ollama import chat, Client
from pdf_db import ConversationDB
import logging
from tqdm import tqdm
import json
import time
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Assistant:
    def __init__(self, pdf_name = "default", model_name="llama3.2:1b"):
        self.model_name = model_name
        self.client = Client(host='http://localhost:11434')
        self.db = ConversationDB(pdf_name = pdf_name)
        self.conversation_history = []
        
        # Context window management
        self.MAX_CONTEXT_TOKENS = 128000  # Maximum context window for Llama 3.2 1B
        self.SAFE_CONTEXT_LIMIT = 64000   # Using 50% of max for safety
        self.MAX_RESPONSE_TOKENS = 100    # Maximum tokens for response
        self.TOKEN_BUFFER = 1000          # Buffer for system messages and formatting
        
        # Log initialization details
        logger.info(f"Initializing Assistant with model: {model_name}")
        logger.info(f"Context window settings:")
        logger.info(f"- Maximum context tokens: {self.MAX_CONTEXT_TOKENS}")
        logger.info(f"- Safe context limit: {self.SAFE_CONTEXT_LIMIT}")
        logger.info(f"- Response token limit: {self.MAX_RESPONSE_TOKENS}")
        
        # Test connection to Ollama
        try:
            start_time = time.time()
            models = self.client.list()
            logger.info(f"Successfully connected to Ollama (took {time.time() - start_time:.2f}s)")
        except Exception as e:
            logger.error("Could not connect to Ollama. Please ensure Ollama is installed and running.")
            raise


    def generate_response(self, user_input):
        """Generate a response using a natural human thought process as Mukul."""
        try:
            print("\n" + "="*50)
            print("Let me think about this...")
            similar_chunks = self.db.get_similar_conversations(user_input, k=10)
            # print(f"simlar chunks are {similar_chunks}")
            # Initialize thought state
            custom_rag_template = f"answer this query: {user_input} based on these contexts {similar_chunks}"
            # custom_rag_template = (
            #     f"Extract all financial terms, their associated numerical values (e.g., percentages, monetary amounts, and time durations) "
            #     f"from the following context and answer this query: {user_input} based on these contexts: {similar_chunks}"
            # )
            # custom_rag_template = (
            #     f"Extract the numerical values associated with the following financial terms from the context: "
            #     f"annual revenue, profit, losses, interest rate, and any other financial terms mentioned. "
            #     f"Answer the query '{user_input}' by including the corresponding financial terms and their numerical values in the response. "
            #     f"Make sure to include the values in the response, but do not limit the answer to only numerical values. "
            #     f"Context for reference: {similar_chunks}"
            # )

            custom_rag_template = (
                f"Act as a financial expert who can understand and interpret financial documents. "
                f"Based on the context provided below, extract and calculate the necessary financial values to answer the user's query accurately. "
                f"The user is asking about a specific financial term, which may include values such as annual revenue, profit, losses, "
                f"interest rates, liabilities, or any other financial term. "
                f"Provide the answer based on the context, ensuring to include all the relevant numerical values, units, and any necessary calculations or clarifications. "
                f"Answer the query '{user_input}' based on the provided context: {similar_chunks}"
            )

            final_response = chat(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": custom_rag_template}
                ],
                options={"temperature": 0.8},
                stream = True
            )
            for chunk in final_response:
                if chunk.message:
                    # print(chunk.message.content)
                    print(chunk.message.content, end="", flush=True)

        except Exception as e:
            error_msg = "I lost my train of thought. Mind if we start over?"
            print(f"\n❌ Sorry, I got distracted: {str(e)}")
            return error_msg


def main():
    print("Initializing Assistant..")
    
    try:
        ai_friend = Assistant("financial_stament_review")
        print("\nHi! I'm Mukul. I'm ready to chat with you!")
        
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'quit':
                print("\nMukul: It was nice talking to you. Goodbye!")
                break
            
            response = ai_friend.generate_response(user_input)
            
    except Exception as e:
        print(f"\nError: {e}")
        print("\nPlease make sure Ollama is installed and running.")

if __name__ == "__main__":
    main() 