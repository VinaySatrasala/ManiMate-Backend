from manim import *

class CrossArrowBoxes(Scene):
    def construct(self):
        # Create the boxes
        box1 = Rectangle(width=2, height=2).set_fill(RED, opacity=0.5).move_to(LEFT * 2)
        box2 = Rectangle(width=2, height=2).set_fill(GREEN, opacity=0.5).move_to(RIGHT * 2)

        # Create arrows
        arrow1 = Arrow(start=box1.get_right(), end=box2.get_left(), buff=0.1)
        arrow2 = Arrow(start=box2.get_left(), end=box1.get_right(), buff=0.1)

        # Add and animate boxes and arrows
        self.play(Create(box1), Create(box2))
        self.play(GrowArrow(arrow1))
        self.play(GrowArrow(arrow2))
        self.wait(1)