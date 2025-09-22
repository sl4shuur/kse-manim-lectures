from manim import *  # type: ignore


class ChatGPTSimulation(Scene):

    TEXT_SIZE = 24
    BOX_OFFSET = 0.5

    def construct(self):
        messages = [
            ("Hello, how can I assist you today?", False),
            ("Can you explain the theory of relativity?", True),
            ("Certainly! The theory of relativity, developed by Albert Einstein, includes both the special and general theories. Special relativity deals with objects moving at constant speeds, particularly those close to the speed of light, and introduces concepts like time dilation and length contraction. General relativity extends these ideas to include gravity, describing it as the curvature of spacetime caused by mass and energy.", False),
            ("That's fascinating! How does time dilation work?", True),
            ("Time dilation occurs when an object is moving at a significant fraction of the speed of light or is in a strong gravitational field. According to special relativity, as an object approaches the speed of light, time appears to slow down for that object relative to a stationary observer. In general relativity, clocks closer to a massive object (like a planet) run slower compared to those further away. This has been confirmed through various experiments, such as observing the decay rates of particles moving at high speeds and using precise atomic clocks on airplanes.", False),
            ("Thank you for the explanation!", True),
            ("You're welcome! If you have any more questions about physics or any other topic, feel free to ask.", False),
        ]

        message = self.get_boxed_message(*messages[0])
        self.play(FadeIn(message))
        self.wait(1)

    def get_boxed_message(self, message: str, is_user: bool) -> VGroup:
        """Create a boxed message with an arrow pointing left or right."""
        text = Text(message, font_size=self.TEXT_SIZE)
        box_color = BLUE_E if is_user else GREEN_E
        box = SurroundingRectangle(
            text,
            corner_radius=0.1,
            color=box_color,
            fill_color=box_color,
            fill_opacity=0.5,
            buff=0.2,
        )

        return VGroup(box, text)
