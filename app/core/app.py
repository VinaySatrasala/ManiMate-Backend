import os
import json
import re
import shutil
import subprocess
import logging
from pathlib import Path
from app.core.app_context import app_context

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Optional: attach a default console handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class App:
    def __init__(self):
        self._chatapp = app_context.chat_application
        self.prompt = app_context.system_prompt
    
    def set_prompt(self, prompt: str):
        self.prompt = prompt

    def run_script(self, script_path: str):
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script file {script_path} does not exist.")

        logger.info(f"Running Manim script: {script_path}")
        try:
            subprocess.run(["manim", "-pql", script_path], check=True, env=os.environ.copy())
            logger.info("Script executed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing script: {e}")

    def move_rendered_video(self, filename: str):
        src = Path(f"media/videos/{filename}/480p15/{filename}.mp4")
        dest_folder = Path("static/videos")
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest = dest_folder / f"{filename}.mp4"

        if not src.exists():
            raise FileNotFoundError(f"Rendered video not found at: {src}")

        shutil.move(str(src), str(dest))
        logger.info(f"Video moved to: {dest}")

    def generate_script(self,user_id : str) -> dict:
        if not self.prompt:
            raise ValueError("Prompt not set. Call set_prompt(prompt) before generate_script().")

        raw_response = self.chatapp.chat(session_id="manim-temp", user_id=user_id,user_input=self.prompt)
        logger.debug("Raw LLM response received.")

        if not raw_response:
            raise ValueError("LLM returned an empty response.")

        if isinstance(raw_response, str):
            raw_response = json.loads(raw_response)

        script_content = raw_response.content
        script_cleaned = re.sub(r"^```python\s*|\s*```$", "", script_content.strip(), flags=re.DOTALL)

        match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)\s*:", script_cleaned)
        if not match:
            raise ValueError("No Manim Scene class found in the script.")

        class_name = match.group(1)
        filename = f"{class_name}.py"
        os.makedirs("scripts", exist_ok=True)
        file_path = os.path.join("scripts", filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script_cleaned)

        logger.info(f"Script saved to {file_path}")
        self.run_script(file_path)
        self.move_rendered_video(class_name)

        return {
            "script_cleaned": script_cleaned,
            "filename": class_name
        }
