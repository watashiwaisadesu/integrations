import openai
from src.core.config import OPENAI_API_KEY
import logging


logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

class AssistantManager:
    def __init__(self, model: str = "gpt-3.5-turbo", assistant_id: str = None, thread_id: str = None) -> None:
        self.client = openai.OpenAI()
        self.model = model
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.assistant = None
        self.thread = None
        self.run = None

        if self.assistant_id:
            print(f"Reusing assistant ID: {self.assistant_id}")
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=self.assistant_id
            )

        if self.thread_id:
            print(f"Reusing thread ID: {self.thread_id}")
            self.thread = self.client.beta.threads.retrieve(
                thread_id=self.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        """
        Create an assistant if one does not already exist.
        """
        if not self.assistant_id:
            assistant_obj = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=self.model,
            )
            self.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"Assistant created with ID: {self.assistant.id}")
        else:
            print(f"Using existing assistant ID: {self.assistant_id}")

        return self.assistant_id

    def set_assistant(self, assistant_id: str):
        """
        Set the assistant in AssistantManager using the provided assistant_id.
        """
        if not assistant_id:
            raise ValueError("Assistant ID is required to set the assistant.")

        self.assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)
        self.assistant_id = assistant_id
        print(f"Assistant retrieved with ID: {self.assistant.id}")



    def create_thread(self):
        """
        Create a new thread if one does not already exist.
        """
        if not self.thread_id:
            thread_obj = self.client.beta.threads.create()
            self.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"Thread created with ID: {self.thread.id}")
        else:
            print(f"Using existing thread ID: {self.thread_id}")

        return self.thread_id

    def set_thread(self, thread_id: str):
        """
        Set the thread in AssistantManager using the provided thread_id.
        """
        if not thread_id:
            raise ValueError("Thread ID is required to set the thread.")

        self.thread = self.client.beta.threads.retrieve(thread_id=thread_id)
        self.thread_id = thread_id
        print(f"Thread retrieved with ID: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        """
        Add a message to the thread.
        """
        if not self.thread:
            raise ValueError("Thread is not initialized. Please create or retrieve a thread before adding a message.")

        try:
            print(f"Adding message to thread: {content}")
            message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content,
            )
            if not message or not hasattr(message, "content"):
                raise ValueError(f"Unexpected response from OpenAI: {message}")
            print(f"Message stored in thread: {message.content}")
            return message
        except Exception as e:
            logger.error(f"Error adding message to thread: {e}")
            raise


    def run_assistant(self, instructions: str) -> dict:
        """
        Run the assistant using the provided instructions on the current thread.
        """
        if not self.thread:
            raise ValueError("Thread is not initialized. Please create or retrieve a thread before running the assistant.")

        if not self.assistant:
            raise ValueError("Assistant is not initialized. Please create or retrieve an assistant before running.")

        try:
            print(f"Running assistant with instructions: {instructions}")
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )
            return {"status": "started", "run_id": self.run.id}
        except Exception as e:
            logger.error(f"Error running assistant: {e}")
            raise

    def wait_for_completion(self):
        """
        Wait until the assistant's run is completed, then process the response.
        """
        if not self.thread or not self.run:
            raise ValueError("Thread or run is not initialized. Please run the assistant first.")

        try:
            while True:
                print("Checking run status...")
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )

                print(f"Run status: {run_status.status}")
                if run_status.status == "completed":
                    print("Run completed. Processing message...")
                    return self.process_message()
                elif run_status.status == "requires_action":
                    # Handle required actions if applicable
                    raise NotImplementedError("Handling required actions is not yet implemented.")
        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            raise

    def process_message(self) -> str:
        """
        Process the latest response message in the thread and return it.
        """
        if not self.thread:
            raise ValueError(
                "Thread is not initialized. Please create or retrieve a thread before processing messages."
            )

        try:
            print("Fetching messages from thread...")
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

            if not messages or not hasattr(messages, "data") or not messages.data:
                raise ValueError("No messages found in the thread.")

            # Get the most recent message
            last_message = messages.data[0]
            response_content = (
                last_message.content[0].text.value if last_message.content else "No response content."
            )

            print(f"Assistant response: {response_content}")
            return response_content
        except Exception as e:
            logger.error(f"Error processing messages: {e}")
            raise



