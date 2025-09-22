from manim import *  # type: ignore

DEBUG_MODE = True


class ChatGPTSimulation(Scene):

    TEXT_SIZE = 24
    BOX_OFFSET = 0.6
    ROUNDNESS = 0.3
    BLUE_E = "#4C97FF"
    GREEN_E = "#5EDF5E"

    upper_edge = UP * 3
    right_edge = RIGHT * 4
    left_edge = LEFT * 3
    big_question_mark = Text("?", font_size=221, color=RED)
    heading = Text("ChatGPT", font_size=52).to_edge(UL)

    def construct(self):

        messages = self._get_messages()
        boxed_messages = self.get_boxed_messages(messages)

        self.play(Write(self.heading))
        self.wait(1)

        # Animate the boxed messages to appear one by one
        self.animate_boxed_messages(boxed_messages, is_skipped=DEBUG_MODE)
        self.wait(1)

        # all the messages are changing to half opacity and appearing big question mark
        self.animate_fade_all_messages(
            boxed_messages, opacity=0.1, is_skipped=DEBUG_MODE
        )
        self.wait(1)

    def _get_boxed_message(self, message: str, is_user: bool) -> VGroup:
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

    def _get_messages(self) -> list[tuple[str, bool]]:
        messages = [
            ("Привіт! Що робиш?", True),
            ("Привіт!\nТа от тригонометрію вивчаю.", False),
            ("О, цікаво! Синус чи косинус?", True),
            ("Та я вже в повному тангегсі... :(", False),
        ]
        return messages

    def get_boxed_messages(self, messages: list[tuple[str, bool]]) -> list[VGroup]:
        """Animate the boxed messages to appear one by one."""
        boxed_messages: list[VGroup] = []
        for msg, is_user in messages:
            boxed_msg = self._get_boxed_message(msg, is_user).align_to(
                self.upper_edge, UP
            )
            if is_user:
                boxed_msg.align_to(self.right_edge, RIGHT)
            else:
                boxed_msg.align_to(self.left_edge, LEFT)
            self.upper_edge = boxed_msg.get_bottom() + DOWN * self.BOX_OFFSET
            boxed_messages.append(boxed_msg)

        return boxed_messages

    def animate_boxed_messages(
        self, boxed_messages: list[VGroup], is_skipped: bool = True
    ):
        """Animate the boxed messages to appear one by one."""
        animation = Succession(
            *[FadeIn(boxed_msg, shift=UP * 0.5) for boxed_msg in boxed_messages],
            lag_ratio=1,
        )

        if is_skipped:
            self.add(*boxed_messages)
        else:
            self.play(animation)

    def animate_fade_all_messages(
        self, boxed_messages: list[VGroup], opacity: float, is_skipped: bool = True
    ):
        """Animate fading all messages to half opacity."""
        msgs_fading_out = [msg.animate(run_time=3).set_opacity(opacity) for msg in boxed_messages]  # type: ignore
        big_question_mark_appear = FadeIn(self.big_question_mark, scale=0.5, run_time=5)

        if is_skipped:
            for msg in boxed_messages:
                msg.set_opacity(opacity)
            self.add(self.big_question_mark)
        else:
            self.play(*msgs_fading_out, big_question_mark_appear)
