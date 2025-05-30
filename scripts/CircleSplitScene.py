from manim import *

class CircleSplitScene(Scene):
    def construct(self):
        # Create a red circle
        red_circle = Circle(radius=1, color=RED).set_fill(RED, opacity=0.5)
        circle_label = Text("red circle", font_size=24).next_to(red_circle, UP)

        # Display initial red circle
        self.play(Create(red_circle), Write(circle_label))
        self.wait(1)

        # Create two semi-circles (upper and lower)
        semi1 = Arc(radius=1, angle=PI, color=GREEN).set_fill(GREEN, opacity=0.5)
        semi2 = Arc(radius=1, start_angle=PI, angle=PI, color=BLUE).set_fill(BLUE, opacity=0.5)

        # Position the semi-circles
        semi1.move_to(red_circle.get_center() + UP * 0.5)
        semi2.move_to(red_circle.get_center() + DOWN * 0.5)

        # Labels for semi-circles
        semi1_label = Text("semi1", font_size=24, color=GREEN).next_to(semi1, UP)
        semi2_label = Text("semi2", font_size=24, color=BLUE).next_to(semi2, DOWN)

        # Animate the splitting of the circle into two semi-circles
        self.play(
            Transform(red_circle, VGroup(semi1, semi2)),
            Transform(circle_label, VGroup(semi1_label, semi2_label))
        )
        self.wait(1)