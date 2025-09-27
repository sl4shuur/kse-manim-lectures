from manim import *  # type: ignore
from src.utils.manim_config import turn_debug_mode_on
from src.utils.config import LOGOS_DIR, IS_DEBUG_MODE_ON


class LogosIntro(Scene):

    OFFSET = 0.5

    def construct(self):
        if IS_DEBUG_MODE_ON:
            turn_debug_mode_on(scene=self, opacity=0.5)

        logos = self.get_logos()

        self.animate_logos(logos, is_skipped=False)
        self.wait()

    def get_logos(self) -> dict[str, SVGMobject]:
        logos = dict()
        logos["chatgpt"] = SVGMobject(LOGOS_DIR / "chatgpt.svg").set_color(WHITE)
        logos["claude"] = SVGMobject(LOGOS_DIR / "claude.svg")
        # gradient colors for the logo
        logos["gemini"] = SVGMobject(LOGOS_DIR / "gemini.svg").set_fill(
            color=["#00BCD4", "#2196F3", "#3F51B5", "#673AB7"],  # type: ignore
            opacity=1,
        )
        logos["deepseek"] = SVGMobject(LOGOS_DIR / "deepseek.svg")
        logos["grok"] = SVGMobject(LOGOS_DIR / "grok.svg").set_color(WHITE)
        return logos

    def animate_logos(self, logos: dict[str, SVGMobject], is_skipped: bool = True):

        intro_anim = DrawBorderThenFill(logos["chatgpt"])

        change_one_anim = AnimationGroup(
            FadeOut(logos["chatgpt"], scale=1.5),
            FadeIn(logos["claude"], scale=0.5),
        )
        change_two_anim = AnimationGroup(
            FadeOut(logos["claude"], scale=1.5),
            FadeIn(logos["gemini"], scale=0.5),
        )
        change_three_anim = AnimationGroup(
            FadeOut(logos["gemini"], scale=1.5),
            FadeIn(logos["grok"], scale=0.5),
        )
        change_four_anim = AnimationGroup(
            FadeOut(logos["grok"], scale=1.5),
            FadeIn(logos["deepseek"], scale=0.5),
        )

        logos["deepseek"].set_z_index(2)  # make sure deepseek is on top

        claude_copy = (
            logos["claude"].copy().next_to(logos["deepseek"], LEFT, buff=self.OFFSET)
        )
        gpt_copy = logos["chatgpt"].copy().next_to(claude_copy, LEFT, buff=self.OFFSET)
        gemini_copy = (
            logos["gemini"].copy().next_to(logos["deepseek"], RIGHT, buff=self.OFFSET)
        )
        grok_copy = logos["grok"].copy().next_to(gemini_copy, RIGHT, buff=self.OFFSET)

        move_gpt_anim = logos["chatgpt"].animate.move_to(gpt_copy)
        move_claude_anim = logos["claude"].animate.move_to(claude_copy)
        move_gemini_anim = logos["gemini"].animate.move_to(gemini_copy)
        logos["grok"].set_width(grok_copy.width * 0.7)
        move_grok_anim = logos["grok"].animate.move_to(grok_copy).set_width(grok_copy.width)

        if is_skipped:
            self.add(logos["claude"])
            return

        self.play(intro_anim)
        self.wait()

        self.play(change_one_anim)
        self.wait()
        self.play(change_two_anim)
        self.wait()
        self.play(change_three_anim)
        self.wait()
        self.play(change_four_anim)
        self.wait(2)

        self.play(move_gpt_anim, move_claude_anim, move_gemini_anim, move_grok_anim)
        self.wait()


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

        if IS_DEBUG_MODE_ON:
            turn_debug_mode_on(scene=self, opacity=0.5)

        messages = self._get_messages()
        boxed_messages = self.get_boxed_messages(messages)

        self.play(Write(self.heading))
        self.wait(1)

        # Animate the boxed messages to appear one by one
        self.animate_boxed_messages(boxed_messages, is_skipped=IS_DEBUG_MODE_ON)
        self.wait(1)

        # all the messages are changing to half opacity and appearing big question mark
        self.animate_fade_all_messages(
            boxed_messages, opacity=0.1, is_skipped=IS_DEBUG_MODE_ON
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


class CosineSimilarity(Scene):
    def construct(self):
        if IS_DEBUG_MODE_ON:
            turn_debug_mode_on(scene=self, opacity=0.5)

        axes = self.get_axes()
        self.play(DrawBorderThenFill(axes))
        self.wait()

        vectors = self.get_vectors(
            labels=["собачка", "кицюня", "добрий", "злий"],
            label_size=33,
            label_buff=0.15,
        )

        self.animate_vectors(vectors, is_skipped=False)

        eng_title = Text("Cosine Similarity", font_size=44).to_edge(LEFT).shift(DOWN)
        ukr_title = Text("косинусна подібність", font_size=28).next_to(
            eng_title, DOWN, buff=0.2, aligned_edge=LEFT
        )

        self.play(
            Succession(
                Write(eng_title),
                Write(ukr_title),
                lag_ratio=1,
            )
        )

        self.wait()

    def get_axes(self, x_length: int = 8, y_length: int = 6) -> Axes:
        step = 1
        x_max = x_length / 2
        y_max = y_length / 2
        axes = Axes(
            x_range=[-x_max, x_max, step],
            y_range=[-y_max, y_max, step],
            x_length=x_length,
            y_length=y_length,
            axis_config={"tip_shape": StealthTip},
        )

        x_label = MathTex("x").next_to(axes.x_axis.get_end(), DR)
        y_label = MathTex("y").next_to(axes.y_axis.get_end(), UL)
        axes.add(x_label, y_label)

        return axes

    def get_vectors(
        self, labels: list[str], label_size: int, label_buff: float
    ) -> list[VGroup]:
        vectors = []
        colors = [YELLOW, PINK, BLUE, RED]

        # first two vectors are close
        coord1 = np.array([2, 1])
        coord2 = np.array([1.8, 1.2])

        # 3rd is orthogonal to the first two
        coord3 = np.array([-1.1, 1.9])

        # 4th is opposite to the third
        coord4 = coord3 * -1

        labels_dirs = [DR, UP, UL, DR]

        # create the vectors

        for i, coord in enumerate([coord1, coord2, coord3, coord4]):
            coord = np.append(coord, 0)  # make it 3D
            vec = VGroup(
                Arrow(
                    start=ORIGIN,
                    end=coord,
                    buff=0,
                    max_tip_length_to_length_ratio=0.1,
                    stroke_width=6,
                    color=colors[i],
                ),
                Text(labels[i], font_size=label_size, color=colors[i]).next_to(
                    coord, labels_dirs[i], buff=label_buff
                ),
            )
            vectors.append(vec)

        return vectors

    def animate_vectors(self, vectors: list[VGroup], is_skipped: bool = True):

        grow_fade_in = lambda vec: LaggedStart(
            GrowArrow(vec[0]), FadeIn(vec[1], scale=0.7), run_time=2, lag_ratio=0.85
        )
        animation = Succession(
            *[grow_fade_in(vec) for vec in vectors],
            lag_ratio=1,
        )

        if is_skipped:
            self.add(*vectors)
        else:
            self.play(animation)

        self.wait()
