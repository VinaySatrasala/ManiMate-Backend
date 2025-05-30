import os
import json
from pathlib import Path
import re
import shutil
from app.services.prompt_processor import PromptProcessor
from app.core.llm_config import LangchainLLMConfig
from app.core.chat_manager import ChatManager
from langchain.chains import ConversationChain

class App:
    def __init__(self):
        self.llm_config = LangchainLLMConfig()
        self.llm = self.llm_config.langchain_llm
        self.chat_manager = ChatManager()

    def set_prompt(self, prompt: str, chat_id: Optional[str] = None):
        """Set the user prompt for visualization."""
        if not chat_id:
            chat_id = self.chat_manager.create_chat()
            
        prompt_processor = PromptProcessor(prompt)
        self.prompt = prompt_processor.build_prompt()
        self.current_chat_id = chat_id
        
        # Add the message to chat history
        self.chat_manager.add_message(chat_id, "human", prompt)

    def run_script(self, script_path: str):
        """Run the generated Manim script using subprocess."""
        import subprocess

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script file {script_path} does not exist.")
        print(script_path)
        try:
            subprocess.run(["manim", "-pql", script_path], check=True, env=os.environ.copy())
            print("✅ Script executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing script: {e}")

    def move_rendered_video(self, filename: str):
        src = Path(f"media/videos/{filename}/480p15/{filename}.mp4")
        dest_folder = Path("static/videos")
        dest_folder.mkdir(parents=True, exist_ok=True)

        dest = dest_folder / f"{filename}.mp4"

        if not src.exists():
            raise FileNotFoundError(f"Rendered video not found at: {src}")

        shutil.move(str(src), str(dest))

    def generate_script(self) -> dict:
        """Generate the Manim script based on the current prompt and save it to a file."""
        if not hasattr(self, 'prompt'):
            raise ValueError("Prompt not set. Please set a prompt before generating the script.")

        # Get chat memory if available
        memory = self.chat_manager.get_memory(self.current_chat_id)
        
        # Create conversation chain with memory
        chain = ConversationChain(
            llm=self.llm,
            memory=memory,
            verbose=True
        )

        # Generate response using the chain
        response = chain.invoke({"input": self.prompt})
        script_content = response["response"]

        # Remove Markdown code block markers
        script_cleaned = re.sub(r"^```python\s*|\s*```$", "", script_content.strip(), flags=re.DOTALL)

        # Find the class name
        match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)\s*:", script_cleaned)
        if not match:
            raise ValueError("No Manim Scene class found in the script.")

        class_name = match.group(1)
        filename = f"{class_name}.py"

        # Ensure the scripts directory exists
        os.makedirs("scripts", exist_ok=True)
        file_path = os.path.join("scripts", filename)

        # Write the script to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script_cleaned)

        print(f"✅ Script saved to {file_path}")
        self.run_script(file_path)
        self.move_rendered_video(class_name)

        # Add AI response to chat history
        self.chat_manager.add_message(self.current_chat_id, "ai", script_cleaned)

        response = {
            "script_cleaned": script_cleaned,
            "filename": class_name,
            "chat_id": self.current_chat_id,
            "messages": [{"role": msg.role, "content": msg.content} 
                        for msg in self.chat_manager.get_chat(self.current_chat_id).messages]
        }
        return response