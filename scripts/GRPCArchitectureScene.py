from manim import *

class GRPCArchitectureScene(Scene):
    def construct(self):
        # Client Rectangle
        client_rect = Rectangle(width=2, height=1, color=BLUE).shift(LEFT * 3)
        client_text = Text("Client", font_size=24).move_to(client_rect.get_center())
        
        # Server Rectangle
        server_rect = Rectangle(width=2, height=1, color=GREEN).shift(RIGHT * 3)
        server_text = Text("Server", font_size=24).move_to(server_rect.get_center())
        
        # Arrows between Client and Server
        request_arrow = Arrow(client_rect.get_right(), server_rect.get_left(), buff=0.1, color=YELLOW)
        response_arrow = Arrow(server_rect.get_left(), client_rect.get_right(), buff=0.1, color=ORANGE)
        
        # Labels for arrows
        request_label = Text("Request", font_size=20).next_to(request_arrow, UP)
        response_label = Text("Response", font_size=20).next_to(response_arrow, DOWN)
        
        # Show all elements
        self.play(FadeIn(client_rect), FadeIn(client_text), FadeIn(server_rect), FadeIn(server_text))
        self.play(GrowArrow(request_arrow), Write(request_label))
        self.wait(1)
        self.play(GrowArrow(response_arrow), Write(response_label))
        self.wait(1)
        
        # Communication concepts
        stub_text = Text("Stub", font_size=20, color=RED).next_to(client_rect, UP)
        server_impl_text = Text("Server\nImplementation", font_size=20, color=RED).next_to(server_rect, UP)
        
        self.play(Write(stub_text), Write(server_impl_text))
        self.wait(2)