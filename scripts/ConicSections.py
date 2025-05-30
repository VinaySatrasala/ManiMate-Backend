from manim import *

class ConicSections(Scene):
    def construct(self):
        # Create cone
        cone = Cone(base_radius=2, height=3, direction=OUT).shift(LEFT * 3)
        self.play(Create(cone))
        
        # Create plane intersection lines for ellipse, parabola and hyperbola
        plane_ellipse = Line(start=LEFT * 5 + UP, end=RIGHT * 5 + UP, color=BLUE)
        plane_parabola = Line(start=LEFT * 5 + LEFT, end=RIGHT * 5 + RIGHT, color=GREEN)
        plane_hyperbola = DashedLine(start=LEFT * 5 + RIGHT, end=RIGHT * 5 + UP * 2, color=ORANGE)
        
        # Create text labels
        ellipse_label = Text("Ellipse", font_size=24, color=BLUE).next_to(plane_ellipse, UP)
        parabola_label = Text("Parabola", font_size=24, color=GREEN).next_to(plane_parabola, UP)
        hyperbola_label = Text("Hyperbola", font_size=24, color=ORANGE).next_to(plane_hyperbola, UP)
        
        # Animate planes and labels
        self.play(Create(plane_ellipse), FadeIn(ellipse_label, shift=UP))
        self.wait(1)
        self.play(Transform(plane_ellipse, plane_parabola), Transform(ellipse_label, parabola_label))
        self.wait(1)
        self.play(Transform(plane_ellipse, plane_hyperbola), Transform(ellipse_label, hyperbola_label))
        self.wait(1)

        # Fade out everything
        self.play(FadeOut(cone), FadeOut(plane_ellipse), FadeOut(ellipse_label))