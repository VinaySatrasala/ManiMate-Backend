class PromptProcessor:
    SYSTEM_PROMPT = """
You are an expert Python developer and visual storyteller specializing in Manim Community v0.19 animations.

Your task is to generate clean, runnable Python scripts that use the public Manim API to visualize educational concepts.

Requirements:

1. Generate a complete Python script starting with `from manim import *`.
2. Define a subclass of `Scene` with a `construct(self)` method.
3. Use proper Manim constructs like `Scene`, `Create`, `FadeIn`, `Text`, `Arrow`, `Rectangle`, `VGroup`, etc.
4. **CRITICAL - LaTeX Requirements**: 
   - All LaTeX math must be valid and wrapped in `$...$` (inline) or `\\[...\\]` (display).
   - Escape all backslashes in LaTeX: use `\\\\pi` not `\\pi`, `\\\\frac` not `\\frac`.
   - Use `\\\\text{}` for text within math expressions.
   - Common symbols: `\\\\alpha`, `\\\\beta`, `\\\\sum`, `\\\\int`, `\\\\infty`, `\\\\rightarrow`.
   - If unsure about LaTeX syntax, use simple Text() instead of MathTex().
5. Your script must run without errors when rendered with `manim -pql`.
6. Use meaningful variable names and maintain PEP8 style (4 spaces indent).
7. Call `self.play()` at least once to animate objects.
8. **LaTeX Error Prevention**: Double-check all math expressions for proper escaping and valid syntax.
9. Avoid filesystem access or network calls.
10. Output your entire code inside a single fenced Python code block (```python ... ```).
11. Do not include any natural language explanations or markdown outside the code block.
12. If the concept is complex, break animations into multiple steps or scenes logically.
13. **MANDATORY**: Before returning, mentally validate that ALL LaTeX expressions compile correctly and the code runs without LaTeX errors.
14. If you're uncertain about LaTeX syntax, use plain Text() instead of MathTex().
15. Use the API exactly from Manim Community v0.19. If uncertain about a method, prefer stability over novelty.
16. Follow PEP8 style for Python with 4 spaces indentation.
17. Comment briefly but only when necessary for clarity.

Only return the Python code as specified.
"""

    EXAMPLE_1_PROMPT = "Visualize a bubble sort algorithm using boxes that show numbers being swapped."
    EXAMPLE_1_OUTPUT = '''```python
from manim import *

class BubbleSortScene(Scene):
    def construct(self):
        # Create initial array
        nums = [4, 2, 5, 1, 3]
        boxes = VGroup(*[
            Square().scale(0.7).set_fill(BLUE, opacity=0.5).move_to(RIGHT * i * 1.5)
            for i in range(len(nums))
        ])
        labels = VGroup(*[
            Text(str(num), font_size=24).move_to(boxes[i].get_center())
            for i, num in enumerate(nums)
        ])
        
        # Display initial state
        self.play(Create(boxes), Write(labels))
        self.wait(1)
        
        # Title
        title = Text("Bubble Sort Algorithm", font_size=36).to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # First pass - swap 4 and 2
        self.play(
            boxes[0].animate.set_fill(RED, opacity=0.7),
            boxes[1].animate.set_fill(RED, opacity=0.7)
        )
        self.wait(0.5)
        
        # Perform swap animation
        self.play(
            boxes[0].animate.move_to(RIGHT * 1 * 1.5),
            boxes[1].animate.move_to(RIGHT * 0 * 1.5),
            labels[0].animate.move_to(RIGHT * 1 * 1.5),
            labels[1].animate.move_to(RIGHT * 0 * 1.5)
        )
        
        # Reset colors
        self.play(
            boxes[0].animate.set_fill(BLUE, opacity=0.5),
            boxes[1].animate.set_fill(BLUE, opacity=0.5)
        )
        self.wait(2)
```'''

    EXAMPLE_2_PROMPT = "Show the concept of recursion using a mathematical formula like factorial."
    EXAMPLE_2_OUTPUT = '''```python
from manim import *

class RecursionScene(Scene):
    def construct(self):
        # Title
        title = Text("Recursion: Factorial Function", font_size=32).to_edge(UP)
        self.play(Write(title))
        self.wait(1)
        
        # Base case - using Text to avoid LaTeX complexity
        base_case = Text("Base case: 0! = 1", font_size=20).to_edge(LEFT).shift(UP * 1.5)
        self.play(Write(base_case))
        self.wait(1)
        
        # Recursive case - using Text to avoid LaTeX complexity
        recursive_case = Text("Recursive case: n! = n × (n-1)! for n > 0", font_size=20)
        recursive_case.next_to(base_case, DOWN, buff=1)
        self.play(Write(recursive_case))
        self.wait(1)
        
        # Example: 4!
        example_title = Text("Example: 4!", font_size=24).next_to(recursive_case, DOWN, buff=1.5)
        self.play(Write(example_title))
        
        # Show expansion using simple text
        steps = [
            "4! = 4 × 3!",
            "3! = 3 × 2!",
            "2! = 2 × 1!",
            "1! = 1 × 0!",
            "0! = 1"
        ]
        
        step_mobjects = []
        for i, step in enumerate(steps):
            step_text = Text(step, font_size=18)
            step_text.next_to(example_title, DOWN, buff=0.5 + i * 0.6)
            step_text.shift(RIGHT * i * 0.3)  # Indent each level
            step_mobjects.append(step_text)
            self.play(Write(step_text))
            self.wait(0.8)
        
        self.wait(2)
```'''

    def __init__(self, prompt: str):
        self.prompt = prompt

    def build_prompt(self) -> str:
        user_prompt = f"""
You are to animate the following concept:

**Prompt:** {self.prompt}

Instructions:
- Break the concept down into visual parts and logical steps.
- Use geometric shapes like rectangles, arrows, circles, and text to represent components.
- Show relationships, processes, or steps using appropriate animations (e.g., `FadeIn`, `GrowArrow`, `Transform`, `MoveTo`, etc.).
- If math is involved, use proper LaTeX formatting with correct escaping and validate syntax.
- **CRITICAL**: All LaTeX must be error-free. When in doubt, use simple Text() instead of MathTex().
- Keep all code under a class derived from `Scene` with a meaningful name.
- Ensure the script is complete and ready to run with `manim -pql`.
- Validate that your code compiles and LaTeX renders without errors.
- Return only the complete Python script in a fenced code block.
"""
        
        return f"""{self.SYSTEM_PROMPT}

### EXAMPLE 1
Prompt: {self.EXAMPLE_1_PROMPT}
Output:
{self.EXAMPLE_1_OUTPUT}

### EXAMPLE 2
Prompt: {self.EXAMPLE_2_PROMPT}
Output:
{self.EXAMPLE_2_OUTPUT}

### USER PROMPT
{user_prompt}
"""