from manim import *  # type: ignore

DEBUG_MODE = True


class ChatGPTSimulation(Scene):

    TEXT_SIZE = 24
    BOX_OFFSET = 0.6
    ROUNDNESS = 0.3
    BLUE_E = "#4C97FF"
    GREEN_E = "#5EDF5E"

    def construct(self):

        heading = Text("ChatGPT", font_size=52).to_edge(UL)

        messages = [
            ("Привіт! Що робиш?", True),
            ("Привіт!\nТа от тригонометрію вивчаю.", False),
            ("О, цікаво! Синус чи косинус?", True),
            ("Та я вже в повному тангегсі... :(", False),
        ]

        upper_edge = UP * 3
        right_edge = RIGHT * 4
        left_edge = LEFT * 3

        big_question_mark = Text("?", font_size=221, color=RED)

        self.play(Write(heading))
        self.wait(1)

        boxed_messages: list[VGroup] = []
        for msg, is_user in messages:
            boxed_msg = self.get_boxed_message(msg, is_user).align_to(upper_edge, UP)
            if is_user:
                boxed_msg.align_to(right_edge, RIGHT)
            else:
                boxed_msg.align_to(left_edge, LEFT)

            self.play(FadeIn(boxed_msg, shift=UP*0.5))
            self.wait(1)
            upper_edge = boxed_msg.get_bottom() + DOWN * self.BOX_OFFSET
            boxed_messages.append(boxed_msg)

        # all the messages are changing to half opacity and appearing big question mark
        msgs_fading_out = [msg.animate(run_time=3).set_opacity(0.1) for msg in boxed_messages] # type: ignore
        big_question_mark_appear = FadeIn(big_question_mark, scale=0.5, run_time=5)
        self.play(*msgs_fading_out, big_question_mark_appear)
        self.wait(1)

    def get_boxed_message(self, message: str, is_user: bool) -> VGroup:
        """Create a boxed message with an arrow pointing left or right."""
        text = Text(message, font_size=self.TEXT_SIZE, line_spacing=0.5)
        box_color = BLUE_E if is_user else GREEN_E
        box = SurroundingRectangle(
            text,
            corner_radius=self.ROUNDNESS,
            color=box_color,
            fill_color=box_color,
            fill_opacity=0.5,
            buff=0.2,
        )

        return VGroup(box, text)
