import json
import pathlib
import re
import sys
from collections import OrderedDict

from lark import Lark, Token, Transformer, Tree, v_args
from lark.reconstruct import Reconstructor

from diagrams import Diagrams

PROJECT_NAME = "docs-cypher"

try:
    PROJECT_ROOT = next(
        path for path in pathlib.Path(__file__).parents if path.name == PROJECT_NAME
    )
    PAGES_DIR = PROJECT_ROOT / "modules" / "ROOT" / "pages"
    EXAMPLES_DIR = PROJECT_ROOT / "modules" / "ROOT" / "examples" / "syntax"
    IMAGES_DIR = PROJECT_ROOT / "modules" / "ROOT" / "images" / "syntax"
except StopIteration:
    raise FileNotFoundError(f"Project root '{PROJECT_NAME}' not found")

with open("bnf-grammar.bnf") as f:
    BNF_GRAMMAR = f.read()

with open("full-grammar.bnf") as f:
    FULL_GRAMMAR = f.read()


def clean_grammar(grammar):
    # Remove one-line comments
    grammar_clean = re.sub(r"(#+|!!)[^\n]+\n+", "", grammar)
    # Remove multi-line comments
    grammar_clean = re.sub(r"/\*{3}.+\*{3}/", "", grammar_clean, flags=re.DOTALL)

    return grammar_clean


def preprocess_grammar(grammar):
    grammar_fixed = clean_grammar(grammar)

    # Replace backslash
    grammar_fixed = re.sub(r'"\\"', r'"\\\\"', grammar_fixed)
    # Replace double quotes
    grammar_fixed = re.sub(r'"""', r'"\""', grammar_fixed)

    # A few hacks to prepare the grammar for cutting
    # Remove non-grammar lines
    grammar_fixed = re.sub(r"any character but:.+\s+\|", "", grammar_fixed)
    # Remove unicode specs
    grammar_fixed = re.sub("unicode: XID_START", '"unicode: XID_START"', grammar_fixed)
    grammar_fixed = re.sub(
        "unicode: XID_CONTINUE", '"unicode: XID_CONTINUE"', grammar_fixed
    )
    # Remove push/pop/check
    grammar_fixed = re.sub(r"push\('\)", r'"PUSH_SINGLE_QUOTE"', grammar_fixed)
    grammar_fixed = re.sub(r'push\("\)', r'"PUSH_DOUBLE_QUOTE"', grammar_fixed)
    grammar_fixed = re.sub(r"pop\(\)", r'"POP_SINGLE_QUOTE"', grammar_fixed)
    grammar_fixed = re.sub(r"check\('\)", r'"CHECK_SINGLE_QUOTE"', grammar_fixed)
    grammar_fixed = re.sub(r'check\("\)', r'"CHECK_DOUBLE_QUOTE"', grammar_fixed)

    return grammar_fixed


def get_rule_name_and_def(tree: Tree):
    # rule
    #   lhs
    #     ruleid      "<" ID ">"
    #   rhs
    #     alternatives
    #       alternative
    #           ruleid      "<" ID ">"
    #       ...

    lhs, rhs = tree.children

    assert len(lhs.children) == 1
    ruleid: Tree = lhs.children[0]
    assert len(ruleid.children) == 1
    id_: Token | Tree[Token] = ruleid.children[0]
    assert isinstance(id_, Token)
    assert id_.type == "ID"

    return id_.value, rhs


def find_definitions(tree: Tree) -> OrderedDict:
    rules = OrderedDict()

    for rule in tree.find_data("rule"):
        rule_name, _ = get_rule_name_and_def(rule)
        rules[rule_name] = rule

    return rules


def find_used_nonterms(tree: Tree, exclude: set) -> list:
    # Extract all nonterminals from a given tree excluding the ones in
    # the `exclude` set
    used_nonterms = []

    for rule in tree.find_data("rule"):
        _, rule_def = get_rule_name_and_def(rule)

        for ruleid in rule_def.find_data("ruleid"):
            nonterm_name = ruleid.children[0].value
            if nonterm_name not in exclude:
                used_nonterms.append(nonterm_name)

    return used_nonterms


def filter_by_nonterms(tree: Tree, nonterms: list, exclude=None) -> Tree:
    if exclude is None:
        exclude = set()

    rules: dict[str, Tree] = OrderedDict.fromkeys(nonterms, Tree("", []))

    for rule in tree.find_data("rule"):
        rule_name, _ = get_rule_name_and_def(rule)

        if rule_name in nonterms and rule_name not in exclude:
            rules[rule_name] = rule

    pruned_tree: Tree = Tree(tree.data, list(rules.values()))
    return pruned_tree


def remove_nonterms(tree: Tree, nonterms):
    rules = []

    for rule in tree.find_data("rule"):
        rule_name, _ = get_rule_name_and_def(rule)

        if rule_name not in nonterms:
            rules.append(rule)

    pruned_tree = Tree(tree.data, rules)
    return pruned_tree


def find_terminals(tree: Tree, terms):
    definitions = find_definitions(tree)
    rules = OrderedDict()

    for term in terms:
        if term in definitions:
            for rule in definitions[term].find_data("text"):
                rules[term] = rule

    return rules


def reconstruct_grammar(tree: Tree):
    nonterm = re.compile(r'(<[^>"]+>)')
    rulehead = re.compile(r'(<[^>"]+>\s*::=\s*)')
    term = re.compile(r'("[^"]+")')

    new_g = Reconstructor(parser).reconstruct(tree, insert_spaces=True)

    # Add spaces around nonterminals
    new_g = nonterm.sub(r" \1 ", new_g)
    # Add newlines to definitions
    new_g = rulehead.sub(r"\n\1 ", new_g)
    # Add spaces around terminals
    new_g = term.sub(r" \1 ", new_g)
    # Remove spurious spaces
    new_g = re.sub(" {2,}", " ", new_g).strip()

    return new_g


class Inliner(Transformer):
    @v_args(tree=True)
    def ruleid(self, ruleid):
        if (
            len(ruleid.children) == 1
            and ruleid.children[0].value in inline_elements_trees
        ):
            return inline_elements_trees[ruleid.children[0].value]
        else:
            return ruleid


if __name__ == "__main__":
    with open(EXAMPLES_DIR / "full-grammar" / "full-grammar.bnf", "w") as fw:
        print("Updating full grammar file")
        full_grammar = clean_grammar(FULL_GRAMMAR)
        fw.write(full_grammar)

    # `maybe_placeholders=False` needed for reconstruction
    parser = Lark(BNF_GRAMMAR, start="rulelist", maybe_placeholders=False)
    tree_full = parser.parse(preprocess_grammar(FULL_GRAMMAR))

    with open("customization.json") as f:
        try:
            customizations = json.load(f)
        except json.JSONDecodeError:
            print(
                "Issues in the customization file. Check that the JSON is complete and correct."
            )
            sys.exit(-1)

    patterns = customizations["patterns"]
    inline_literals = customizations["inline_literals"]
    links = customizations["links"]

    all_missing_links = set()

    for pattern in patterns:
        pattern_name = pattern["name"]
        pattern_category = pattern["category"]
        start_nonterm = pattern["start_nonterm"]
        exclude = set(pattern["exclude"])

        print(f"Updating snippet: '{pattern_name}'")

        filtered_tree = filter_by_nonterms(tree_full, [start_nonterm], exclude=exclude)

        defs = find_definitions(filtered_tree).keys()
        used_defs = [start_nonterm] + find_used_nonterms(filtered_tree, exclude=exclude)

        # print("Defs", defs, "Used defs", used_defs)

        MAX_ITER = 100
        num_iter = 0

        while set(defs) != set(used_defs) and num_iter <= MAX_ITER:
            filtered_tree = filter_by_nonterms(tree_full, used_defs, exclude=exclude)

            defs = find_definitions(filtered_tree).keys()
            used_defs += find_used_nonterms(filtered_tree, exclude=exclude)

            # print("Defs", defs, "Used defs", used_defs)

            num_iter += 1

        if num_iter > MAX_ITER:
            print("Max iterations exceeded. Check the grammar and the code.")

        inline_elements = set(inline_literals)
        inline_elements_trees = find_terminals(filtered_tree, inline_literals)

        transformed_tree = Inliner().transform(
            remove_nonterms(filtered_tree, inline_elements)
        )
        reconstructed = reconstruct_grammar(transformed_tree)

        ### Diag
        diag = Diagrams(transformed_tree, {})
        svg = diag.get_svg()

        svg_path = IMAGES_DIR / pattern_category
        svg_path.mkdir(exist_ok=True)
        svg_file = f"{pattern_name}.svg"
        with open(svg_path / svg_file, "w") as fw:
            fw.write(svg)

        bnf_path = EXAMPLES_DIR / pattern_category
        bnf_path.mkdir(exist_ok=True)
        processed_grammar_file = f"{pattern_name}.bnf"
        with open(bnf_path / processed_grammar_file, "w") as fw:
            for link in links:
                symbol, exclusions = (
                    f'<{link["symbol"]}>',
                    link["exclusions"],
                )
                symbol_defined = re.search(f"^{symbol}", reconstructed, re.MULTILINE)

                # If the symbol appears as a nonterminal definition, do not replace with link
                if processed_grammar_file not in exclusions and symbol_defined is None:
                    xref_or_link = link.get("xref")
                    if xref_or_link is not None:
                        xref_or_link = f"xref:{xref_or_link}[{symbol}]"
                    else:
                        xref_or_link = link["link"]
                        xref_or_link = f"link:{xref_or_link}[{symbol}]"

                    reconstructed = re.sub(
                        f"{symbol}", xref_or_link, reconstructed
                    )

            fw.write(reconstructed)

        all_links = {link["symbol"] for link in links}
        missing_links = exclude.difference(all_links)
        if missing_links:
            print(" * Missing links:", missing_links)
            all_missing_links.update(missing_links)

    if all_missing_links:
        print(f"There are {len(all_missing_links)} missing links")