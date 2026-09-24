import re
from inspect import cleandoc
from io import StringIO
from itertools import batched

from lark import Lark
from railroad import (  # type: ignore
    Choice,
    Diagram,
    NonTerminal,
    OneOrMore,
    Optional,
    Sequence,
    Stack,
    Start,
    Terminal,
)

with open("bnf-grammar.bnf") as f:
    BNF_GRAMMAR = f.read()

SVG_PATTERN = '<svg class="railroad-diagram" viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">{content}{style}</svg>'

with open("svg-style.css") as f:
    SVG_STYLE = f"""<style>
        /* <![CDATA[ */
        {f.read()}
        /* ]]> */
    </style>"""


class Diagrams:
    def _preprocess_grammar(self, grammar):
        # Remove one-line comments
        grammar_fixed = re.sub(r"(#+|!!)[^\n]+\n", "", grammar)
        # Remove multi-line comments
        return re.sub(r"/\*{3}.+\*{3}/", "", grammar_fixed, flags=re.DOTALL)

    def _process_rule(self, rule):
        LIMIT_SEQUENCE_LEN = False
        MAX_IN_SEQUENCE = 1

        if rule.data.value == "alternatives":
            alts = []
            for alt in rule.children:
                alts.append(self._process_rule(alt))
            return Choice(0, *alts)
        elif rule.data.value in ("alternative", "grouping"):
            elems = []
            for elem in rule.children:
                elems.append(self._process_rule(elem))
            if LIMIT_SEQUENCE_LEN and len(elems) > MAX_IN_SEQUENCE:
                sequences = [Sequence(*batch) for batch in batched(elems, MAX_IN_SEQUENCE)]
                return Stack(*sequences)
            else:
                return Sequence(*elems)
        elif rule.data.value == "optional":
            return Optional(self._process_rule(rule.children[0]))
        # elif rule.data.value == "grouping":
        #     return Group(process_rule(rule.children[0]))
        elif rule.data.value == "oneormore":
            return OneOrMore(self._process_rule(rule.children[0]))
        elif rule.data.value == "text":
            text = rule.children[0].value.strip("\"")
            # Custom rule to deal with "placeholders"
            if text.startswith("___") and text.endswith("___"):
                return Terminal(text.strip("___"), cls="it")
            else:
                return Terminal(text)
        elif rule.data.value == "ruleid":
            name = rule.children[0].value

            if name in self.links:
                return NonTerminal(name, title=name, href=self.links[name])
            else:
                return NonTerminal(name, title=name)
        else:
            raise ValueError("Non-matching:", rule.data.value)

    def __init__(self, tree, links):
        self.diagrams = []
        self.links = links

        for rule in tree.children:
            lhs, rhs = rule.children

            assert len(lhs.children) == 1
            assert lhs.children[0].children[0].type == "ID"

            rule_name = lhs.children[0].children[0].value

            assert len(rhs.children) == 1

            diagram = Diagram(
                Start(label=rule_name), self._process_rule(rhs.children[0])
            )

            s = StringIO()
            diagram.writeSvg(s.write)
            s.seek(0)
            self.diagrams.append(s.read())

    def get_svg(self):
        max_width, height = 0, 0
        translated_elements = []

        for i, diagram in enumerate(self.diagrams):
            svg_object = re.sub(
                r"<svg [^>]+>\s*(.+)</svg>", r"\1", diagram, flags=re.DOTALL
            )
            translated = f'<g transform="translate(0, {height})">{svg_object}</g>'
            translated_elements.append(translated)

            m = re.match(
                r'<svg .+ height="(?P<height>[\d.]+)" .+ width="(?P<width>[\d.]+)">',
                diagram,
            )
            height += float(m.group("height"))
            width = float(m.group("width"))

            if width > max_width:
                max_width = width

        # Stacking
        return SVG_PATTERN.format(
            width=max_width,
            height=height,
            content="\n".join(translated_elements),
            style=cleandoc(SVG_STYLE),
        )
