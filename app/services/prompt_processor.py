class PromptProcessor:
    SYSTEM_PROMPT = """
You are an expert Python developer and visual storyteller specializing in Manim animations.

Your task is to:
1. Interpret user prompts as educational visualizations (e.g., client-server architecture, sorting algorithms, AI concepts, etc.).
2. Generate a complete and functional **Manim Python script** (v0.18+).
3. Use the appropriate Manim constructs (`Scene`, `Create`, `Text`, `Arrow`, `Rectangle`, `VGroup`, `FadeIn`, etc.) to animate ideas clearly.
4. Keep code clean, modular, and minimal.
5. Use meaningful variable names, spacing, and animation timing.
6. DO NOT add markdown, explanations, or natural language in your output — return **only raw Python code**.
"""

    EXAMPLE_1_PROMPT = "Visualize a bubble sort algorithm using boxes that show numbers being swapped."
    EXAMPLE_1_OUTPUT = '''
from manim import *

class BubbleSortScene(Scene):
    def construct(self):
        nums = [4, 2, 5, 1, 3]
        boxes = VGroup(*[
            Square().scale(0.7).set_fill(BLUE, opacity=0.5).move_to(RIGHT * i)
            for i in range(len(nums))
        ])
        labels = VGroup(*[
            Text(str(num), font_size=24).move_to(boxes[i].get_center())
            for i, num in enumerate(nums)
        ])
        self.play(Create(boxes), Write(labels))
        self.wait(1)

        # Swap 4 and 2
        self.play(boxes[0].animate.move_to(RIGHT * 1), boxes[1].animate.move_to(RIGHT * 0))
        self.play(Swap(labels[0], labels[1]))
        self.wait(1)
    '''

    def __init__(self, prompt: str):
        self.prompt = prompt


    def build_prompt(self) -> str:
        user_prompt = f"""
You are to animate the following concept:

**Prompt:** {self.prompt}

Instructions:
- Break the concept down into visual parts.
- Use geometric shapes like rectangles, arrows, and text.
- Show relationships or steps using animation (e.g., `FadeIn`, `GrowArrow`, `MoveTo`, etc.).
- Keep all code under a class derived from `Scene`, ready to run with Manim.
- Return only the complete Python script.
"""
        return f"""{self.SYSTEM_PROMPT}

### EXAMPLE 1
Prompt: {self.EXAMPLE_1_PROMPT}
Output:
{self.EXAMPLE_1_OUTPUT}

### USER PROMPT
{user_prompt}
"""
