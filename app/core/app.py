import os
import json
import re
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
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
    def __init__(self, max_retry_attempts: int = 3):
        self._chatapp = app_context.chat_application
        self.prompt = app_context.system_prompt
        self.max_retry_attempts = max_retry_attempts
    
    def set_prompt(self, prompt: str):
        self.prompt = prompt

    def run_script(self, script_path: str) -> Tuple[bool, Optional[str]]:
        """
        Run a script and return success status and error message if any.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        if not os.path.exists(script_path):
            error_msg = f"Script file {script_path} does not exist."
            logger.error(error_msg)
            return False, error_msg

        logger.info(f"Running Manim script: {script_path}")
        try:
            result = subprocess.run(
                ["manim", "-pql", script_path], 
                check=True, 
                env=os.environ.copy(),
                capture_output=True,
                text=True
            )
            logger.info("Script executed successfully.")
            
            # Additional check: verify that the video was actually created
            # Extract class name from script to check if video exists
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)\s*:", script_content)
            if match:
                class_name = match.group(1)
                script_filename = os.path.basename(script_path)
                folder_name = script_filename.replace('.py', '')
                expected_video_path = Path(f"media/videos/{folder_name}/480p15/{class_name}.mp4")
                
                if not expected_video_path.exists():
                    error_msg = f"Script ran without errors but no video was generated at: {expected_video_path}"
                    logger.error(error_msg)
                    return False, error_msg
            
            return True, None
        except subprocess.CalledProcessError as e:
            error_msg = f"Error executing script: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}"
            logger.error(error_msg)
            return False, error_msg

    def move_rendered_video(self, class_name: str, script_filename: str):
        """
        Move rendered video from Manim's output directory to static folder.
        
        Args:
            class_name: The Scene class name (for final video name)
            script_filename: The actual script filename used (may include attempt suffix)
        """
        # Manim creates folder based on script filename (without .py extension)
        folder_name = script_filename.replace('.py', '')
        src = Path(f"media/videos/{folder_name}/480p15/{class_name}.mp4")
        dest_folder = Path("static/videos")
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest = dest_folder / f"{class_name}.mp4"

        if not src.exists():
            raise FileNotFoundError(f"Rendered video not found at: {src}")

        shutil.move(str(src), str(dest))
        logger.info(f"Video moved to: {dest}")

    def create_error_correction_prompt(self, original_code: str, error_message: str, attempt_number: int) -> str:
        """
        Create a prompt for the LLM to fix the code based on the error.
        """
        return f"""
The following Manim script failed to execute with an error. Please fix the code and return only the corrected Python code without any explanations or markdown formatting.

ORIGINAL CODE:
{original_code}

ERROR MESSAGE:
{error_message}

ATTEMPT NUMBER: {attempt_number}/{self.max_retry_attempts}

Requirements:
1. Fix the specific error mentioned above
2. Ensure the code follows Manim best practices
3. The class should inherit from Scene
4. Return only the corrected Python code without ```python``` blocks
5. Make sure all imports are included
6. Test that the logic is sound before responding

CORRECTED CODE:
"""

    def fix_script_with_llm(self, script_content: str, error_message: str, session_id: str, user_id: str, attempt_number: int) -> str:
        """
        Use LLM to fix the script based on the error message.
        """
        correction_prompt = self.create_error_correction_prompt(script_content, error_message, attempt_number)
        
        logger.info(f"Attempting to fix script with LLM (attempt {attempt_number}/{self.max_retry_attempts})")
        
        raw_response = self._chatapp.chat(
            session_id=session_id, 
            user_id=user_id, 
            user_input=correction_prompt
        )
        
        if not raw_response:
            raise ValueError("LLM returned an empty response for error correction.")

        if isinstance(raw_response, str):
            raw_response = json.loads(raw_response)

        corrected_content = raw_response.content
        # Clean any remaining markdown formatting
        corrected_cleaned = re.sub(r"^```python\s*|\s*```$", "", corrected_content.strip(), flags=re.DOTALL)
        
        return corrected_cleaned

    def extract_and_validate_script(self, script_content: str) -> Tuple[str, str]:
        """
        Extract class name and validate the script structure.
        
        Returns:
            Tuple[str, str]: (class_name, cleaned_script)
        """
        script_cleaned = re.sub(r"^```python\s*|\s*```$", "", script_content.strip(), flags=re.DOTALL)

        match = re.search(r"class\s+(\w+)\s*\(\s*Scene\s*\)\s*:", script_cleaned)
        if not match:
            raise ValueError("No Manim Scene class found in the script.")

        class_name = match.group(1)
        return class_name, script_cleaned

    def save_script(self, script_content: str, class_name: str, attempt_number: int = 0) -> str:
        """
        Save script to file with optional attempt number suffix.
        """
        suffix = f"_attempt_{attempt_number}" if attempt_number > 0 else ""
        filename = f"{class_name}{suffix}.py"
        
        os.makedirs("scripts", exist_ok=True)
        file_path = os.path.join("scripts", filename)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        logger.info(f"Script saved to {file_path}")
        return file_path

    def generate_script(self, session_id: str, user_id: str) -> Dict:
        """
        Generate and execute script with automatic error correction.
        """
        if not self.prompt:
            raise ValueError("Prompt not set. Call set_prompt(prompt) before generate_script().")

        # Generate initial script
        raw_response = self._chatapp.chat(session_id=session_id, user_id=user_id, user_input=self.prompt)
        logger.debug("Raw LLM response received.")

        if not raw_response:
            raise ValueError("LLM returned an empty response.")

        if isinstance(raw_response, str):
            raw_response = json.loads(raw_response)

        script_content = raw_response.content
        
        # Attempt to run script with retries
        for attempt in range(self.max_retry_attempts):
            try:
                # Extract and validate script
                class_name, script_cleaned = self.extract_and_validate_script(script_content)
                
                # Save script
                file_path = self.save_script(script_cleaned, class_name, attempt)
                
                # Try to run script
                success, error_message = self.run_script(file_path)
                
                if success:
                    # Script ran successfully, move video
                    script_filename = os.path.basename(file_path)
                    self.move_rendered_video(class_name, script_filename)
                    logger.info(f"Script executed successfully on attempt {attempt + 1}")
                    
                    return {
                        "script_cleaned": script_cleaned,
                        "filename": class_name,
                        "attempts": attempt + 1,
                        "success": True
                    }
                else:
                    # Script failed, try to fix it
                    if attempt < self.max_retry_attempts - 1:  # Don't fix on last attempt
                        logger.warning(f"Script failed on attempt {attempt + 1}, trying to fix...")
                        script_content = self.fix_script_with_llm(
                            script_cleaned, 
                            error_message, 
                            session_id, 
                            user_id, 
                            attempt + 1
                        )
                        # Continue to next iteration to run the fixed script
                        continue
                    else:
                        # Last attempt failed
                        logger.error(f"Script failed after {self.max_retry_attempts} attempts")
                        return {
                            "script_cleaned": script_cleaned,
                            "filename": class_name,
                            "attempts": attempt + 1,
                            "success": False,
                            "final_error": error_message
                        }
                        
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed with exception: {e}")
                if attempt < self.max_retry_attempts - 1:
                    # Try to fix the script
                    try:
                        script_content = self.fix_script_with_llm(
                            script_content, 
                            str(e), 
                            session_id, 
                            user_id, 
                            attempt + 1
                        )
                        # Continue to next iteration to run the fixed script
                        continue
                    except Exception as fix_error:
                        logger.error(f"Failed to fix script: {fix_error}")
                        continue
                else:
                    # Final attempt failed
                    return {
                        "script_cleaned": script_content,
                        "filename": "unknown",
                        "attempts": attempt + 1,
                        "success": False,
                        "final_error": str(e)
                    }

        # Should not reach here, but just in case
        return {
            "script_cleaned": script_content,
            "filename": "unknown", 
            "attempts": self.max_retry_attempts,
            "success": False,
            "final_error": "Maximum attempts reached"
        }