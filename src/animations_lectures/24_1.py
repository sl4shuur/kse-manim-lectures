from manim import *  # type: ignore
from src.utils.manim_config import turn_debug_mode_on, UkrainianTexTemplate
from src.utils.config import LOGOS_DIR, IS_DEBUG_MODE_ON
import numpy as np


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
        move_grok_anim = (
            logos["grok"].animate.move_to(grok_copy).set_width(grok_copy.width)
        )

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


class IntroToTrigonometry(Scene):

    colors = [BLUE, RED, GREEN]
    edge_labels = ["прилеглий", "протилежний", "гіпотенуза"]

    a = ORIGIN
    b = RIGHT * 3
    c = b + UP * 4

    def construct(self):
        if IS_DEBUG_MODE_ON:
            self.debug_plane = turn_debug_mode_on(scene=self, opacity=0.5)

        self.triangle = self.create_triangle(self.a, self.b, self.c, stroke_width=6)
        triangle = self.triangle
        triangle.shift(LEFT * 4 + DOWN * 1.5)
        self.animate_triangle(triangle, is_skipped=IS_DEBUG_MODE_ON)

        self.animate_alpha_label(triangle, alpha_label_size=69, is_skipped=IS_DEBUG_MODE_ON)

        self.animate_sides_labels(triangle, text_size=33, is_skipped=IS_DEBUG_MODE_ON)

        self.animate_sincos_formulas(is_skipped=IS_DEBUG_MODE_ON)

        els_to_leave = [self.debug_plane, self.triangle] if IS_DEBUG_MODE_ON else [self.triangle]

        self.animate_remove_all_elements(els_to_leave=els_to_leave, is_skipped=False)  # type: ignore

        self.wait()

    def create_triangle(
        self, a: np.ndarray, b: np.ndarray, c: np.ndarray, stroke_width: int
    ) -> VGroup:
        line1 = Line(a, b, color=WHITE, stroke_width=stroke_width)
        line2 = Line(b, c, color=WHITE, stroke_width=stroke_width)
        line3 = Line(c, a, color=WHITE, stroke_width=stroke_width)

        adj_right_angle = RightAngle(line1, line2, length=0.5, color=WHITE, quadrant=(-1, 1))  # type: ignore

        triangle = VGroup(line1, line2, line3, adj_right_angle)
        return triangle

    def animate_triangle(self, triangle: VGroup, is_skipped: bool = True):
        right_angle = triangle[3]

        if is_skipped:
            self.add(triangle)
        else:
            self.play(
                LaggedStart(
                    AnimationGroup(*[Create(line) for line in triangle[:3]]),  # type: ignore
                    Create(right_angle),  # type: ignore
                    lag_ratio=1,
                )
            )
        self.wait()

    def animate_alpha_label(
        self,
        triangle: VGroup,
        alpha_label_size: int = 48,
        buff: float = 0.4,
        is_skipped: bool = True,
    ):
        line1 = triangle[0]
        line2 = triangle[1]
        line3 = triangle[2]

        angle = Angle(line1, line3, radius=1, color=WHITE, quadrant=(1, -1))  # type: ignore
        alpha = MathTex(r"\alpha", font_size=alpha_label_size, color=WHITE)
        
        arc_center = line1.get_start()
        p = line2.point_from_proportion(0.35)
        direction = p - arc_center
        direction /= np.linalg.norm(direction)

        alpha.move_to(arc_center + direction * (angle.radius + buff))

        if is_skipped:
            self.add(alpha, angle)
        else:
            self.play(LaggedStart(Create(angle), Write(alpha), lag_ratio=1))

        triangle.add(angle, alpha)
        self.wait()

    def animate_sides_labels(self, triangle: VGroup, text_size: int = 36, is_skipped: bool = True):
        close_cathetus = triangle[0]
        far_cathetus = triangle[1]
        hypotenuse = triangle[2]

        text_close, text_far, text_hyp = [
            Text(text, font_size=text_size, color=color)
            for text, color in zip(self.edge_labels, self.colors)
        ]

        text_close.next_to(close_cathetus.get_center(), DOWN, buff=0.2)

        # rotate the far cathetus and hypotenuse labels to match the line angle
        angle_far = angle_of_vector(far_cathetus.get_vector())
        text_far.rotate(angle_far).next_to(far_cathetus.get_center(), RIGHT, buff=0.2)

        # get normal vector-direction for the hypotenuse label
        angle_hyp = angle_of_vector(hypotenuse.get_vector())
        normal_hyp = angle_hyp - PI / 2
        normal_vec = np.array([np.cos(normal_hyp), np.sin(normal_hyp), 0])
        normal_vec /= np.linalg.norm(normal_vec)

        # make sure the angle is within -PI/2 to PI/2 range
        if abs(angle_hyp) > PI/2:
            angle_hyp += PI

        text_hyp.rotate(angle_hyp).move_to(hypotenuse.point_from_proportion(0.45) + normal_vec * 0.33)

        if is_skipped:
            [edge.set_color(color) for edge, color in zip(triangle[:3], self.colors)]
            self.add(text_close, text_far, text_hyp)
            return
        
        else:
            anims = [LaggedStart(
                edge.animate.set_color(color),  # type: ignore
                Write(text),
                lag_ratio=1,
            ) for edge, color, text in zip(triangle[:3], self.colors, [text_close, text_far, text_hyp])]
            self.play(Succession(*anims, lag_ratio=1))
        self.wait()

    def animate_sincos_formulas(self, text_size = DEFAULT_FONT_SIZE, is_skipped: bool = True):

        sin_formula = Tex(r"$\sin(\alpha) = \frac{\text{протилежний}}{\text{гіпотенуза}}$", font_size=text_size, tex_template=UkrainianTexTemplate)
        cos_formula = Tex(r"$\cos(\alpha) = \frac{\text{прилеглий}}{\text{гіпотенуза}}$", font_size=text_size, tex_template=UkrainianTexTemplate)

        sin_formula.to_edge(UR, buff=1).shift(LEFT)
        cos_formula.next_to(sin_formula, DOWN, buff=0.5).align_to(sin_formula, LEFT)
        # show index for the fraction
        # https://docs.manim.community/en/stable/reference/manim.utils.debug.html
        sin_indices = index_labels(sin_formula[0])
        cos_indices = index_labels(cos_formula[0])

        # color everything in black first (dumb approach, but works)

        sin_formula[0][7:].set_color(BLACK)
        cos_formula[0][7:].set_color(BLACK)

        if is_skipped:
            # color the text in the formula by indices
            sin_formula[0][18].set_color(WHITE)  # frac line
            sin_formula[0][7:18].set_color(self.colors[1])  # протилежний
            sin_formula[0][19:].set_color(self.colors[2])  # гіпотенуза

            cos_formula[0][16].set_color(WHITE)  # frac line
            cos_formula[0][7:16].set_color(self.colors[0])  # прилеглий
            cos_formula[0][17:].set_color(self.colors[2])  # гіпотенуза
            self.add(sin_formula, sin_indices, cos_formula, cos_indices)
        else:
            # step by step animation
            # 1. write sin formula
            self.play(Write(sin_formula))
            self.wait()
            # 2. appear frac line
            self.play(sin_formula[0][18].animate.set_color(WHITE))
            self.wait()
            # 3. color the text in the formula by indices
            self.play(sin_formula[0][7:18].animate.set_color(self.colors[1]))  # протилежний
            self.wait()
            self.play(sin_formula[0][19:].animate.set_color(self.colors[2]))  # гіпотенуза
            self.wait(2)
            # 4. do the same for cos formula
            self.play(Write(cos_formula))
            self.wait()
            self.play(cos_formula[0][16].animate.set_color(WHITE))
            self.wait()
            self.play(cos_formula[0][7:16].animate.set_color(self.colors[0]))  # прилеглий
            self.wait()
            self.play(cos_formula[0][17:].animate.set_color(self.colors[2]))  # гіпотенуза
        self.wait()

        self.animate_cossin_hack(cos_formula=cos_formula, sin_formula=sin_formula, text_size=text_size+10, is_skipped=is_skipped)

        self.wait()

    def animate_cossin_hack(self, cos_formula: Tex, sin_formula: Tex, buff: float = 1.3, text_size = DEFAULT_FONT_SIZE, is_skipped: bool = True):
        cos_text = MathTex(r"\cos", font_size=text_size)
        cos_text.next_to(cos_formula, DOWN, buff=buff, aligned_edge=LEFT)

        sin_text = MathTex(r"\sin", font_size=text_size)
        sin_text.next_to(cos_text, RIGHT, buff=0.5, aligned_edge=DOWN)

        cossin_before = VGroup(cos_text, sin_text)
        cossin_after = MathTex(r"\text{cossin}", font_size=text_size).move_to(cossin_before)
        cosin_text = MathTex(r"\text{cosin}", font_size=text_size).move_to(cossin_after)

        # color letter s in yellow
        cosin_text[0][2].set_color(YELLOW)

        # now order intuitively
        reduce_size = 12
        ordered_cos = Tex(r"\text{1. cos → прилеглий катет}", font_size=text_size - reduce_size, tex_template=UkrainianTexTemplate)
        ordered_cos.next_to(cosin_text, DOWN, buff=0.5).align_to(cos_formula, LEFT)
        ordered_sin = Tex(r"\text{2. sin → протилежний}", font_size=text_size - reduce_size, tex_template=UkrainianTexTemplate)
        ordered_sin.next_to(ordered_cos, DOWN, buff=0.3, aligned_edge=LEFT)

        # set black color first
        ordered_cos[0][5:].set_color(BLACK)
        ordered_sin[0][5:].set_color(BLACK)


        if is_skipped:
            ordered_cos.set_color(self.colors[0])
            ordered_sin.set_color(self.colors[1])

            self.add(cosin_text, ordered_cos, ordered_sin)

        else:
            self.play(Write(cossin_before))
            self.wait()
            self.play(TransformMatchingShapes(cossin_before, cossin_after))
            self.wait()
            self.play(Transform(cossin_after, cosin_text))
            self.wait(2)
            self.play(Succession(
                Write(ordered_cos), Write(ordered_sin), lag_ratio=1
            ))
            self.wait()

            # indicate first letters
            sf = 1.5
            self.play(Succession(
                Indicate(ordered_cos[0][2], color=BLUE, scale_factor=sf),  # type: ignore
                Indicate(ordered_sin[0][2], color=RED, scale_factor=sf),  # type: ignore
                lag_ratio=1,
            ))
            self.wait()

            # now indicate the cathetus of the triangle
            triangle = self.triangle
            self.play(Succession(
                Indicate(triangle[0], color=YELLOW),  # type: ignore
                Indicate(triangle[1], color=YELLOW),  # type: ignore
                lag_ratio=1,
            ))
            self.wait()

            # color the text in the formulas to WHITE (appear)
            self.play(Succession(*[tex[0][5:].animate.set_color(WHITE) for tex in [ordered_cos, ordered_sin]], lag_ratio=1))  # type: ignore
            self.wait()
            # color the whole text in the formulas by intuitive colors
            self.play(Succession(*[tex.animate.set_color(self.colors[i]) for i, tex in enumerate([ordered_cos, ordered_sin])], lag_ratio=1))  # type: ignore
            self.wait()
            # indicate cos in cos_formula and the numerator
            self.play(Succession(Indicate(cos_formula[0][:3], color=BLUE), Indicate(cos_formula[0][7:16]), lag_ratio=1))  # type: ignore
            self.wait()
            # indicate sin in sin_formula and the numerator
            self.play(Succession(Indicate(sin_formula[0][:3], color=RED), Indicate(sin_formula[0][7:18]), lag_ratio=1))  # type: ignore
        self.wait()

    def animate_remove_all_elements(self, els_to_leave: list[VMobject], is_skipped: bool = True):
        mobject_to_dissolve = [m for m in self.mobjects if m not in els_to_leave]
        triangle_shift = RIGHT * 2
        if is_skipped:
            self.remove(*mobject_to_dissolve)
            self.triangle.shift(triangle_shift)
        else:
            self.play(FadeOut(Group(*mobject_to_dissolve)))
            self.wait()
            # move the remaining elements to the center
            self.play(self.triangle.animate.shift(triangle_shift))
        self.wait()

    def animate_trig_similarity(self, triangle: VGroup, is_skipped: bool = True):
        pass