from manim import *

class MergeSortScene(Scene):
    def construct(self):
        # Initial list of numbers
        nums = [38, 27, 43, 3, 9, 82, 10]
        
        # Create rectangles to represent elements
        boxes = VGroup(*[
            Rectangle(height=0.8, width=1.2).set_fill(BLUE, opacity=0.5).move_to(RIGHT * i)
            for i in range(len(nums))
        ])
        labels = VGroup(*[
            Text(str(num), font_size=24).move_to(boxes[i].get_center())
            for i, num in enumerate(nums)
        ])
        
        self.play(Create(boxes), Write(labels))
        self.wait(1)

        # Split into halves: visualization
        left_rect = SurroundingRectangle(VGroup(*boxes[:4]), color=YELLOW)
        right_rect = SurroundingRectangle(VGroup(*boxes[4:]), color=GREEN)
        
        half_text_left = Text("Left Half", font_size=24).next_to(left_rect, UP)
        half_text_right = Text("Right Half", font_size=24).next_to(right_rect, UP)

        self.play(Create(left_rect), Create(right_rect))
        self.play(Write(half_text_left), Write(half_text_right))
        self.wait(1)

        # Further split visualization
        left_split_rect = SurroundingRectangle(VGroup(*boxes[:2]), color=ORANGE)
        right_split_rect = SurroundingRectangle(VGroup(*boxes[2:4]), color=ORANGE)
        half_text_left_next = Text("Split Again", font_size=24).next_to(left_split_rect, UP)

        self.play(Create(left_split_rect), Create(right_split_rect))
        self.play(Write(half_text_left_next))
        self.wait(1)

        # Show merging process
        merge_text = Text("Merge Sorted Halves", font_size=24).to_edge(DOWN)
        self.play(Write(merge_text))
        self.wait(1)
        
        # Illustrate merging with arrows
        sorted_boxes = VGroup(*[
            Rectangle(height=0.8, width=1.2).set_fill(GREEN, opacity=0.5).move_to(RIGHT * (i + 0.5))
            for i in range(len(nums))
        ])
        sorted_labels = VGroup(*[
            Text(str(num), font_size=24).move_to(sorted_boxes[i].get_center())
            for i, num in enumerate(sorted([38, 27, 43, 3, 9, 82, 10])) # Simulate sorted list
        ])
        
        for i in range(len(nums)):
            self.play(FadeIn(sorted_boxes[i]), FadeIn(sorted_labels[i]))

        self.wait(2)