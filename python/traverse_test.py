from typing import List

from traverse import traverse_and_execute, traverse_and_replace


def test_traverse_and_execute() -> None:
    text: List[str] = []

    def capture_text(element):
        if element.text:
            text.append(element.text)

    traverse_and_execute("<p><i>Hello</i> <strong>world</strong></p>", capture_text)

    assert text == ["Hello", "world"]


def test_traverse_and_replace_text() -> None:
    html = traverse_and_replace("Hello", lambda e: "Goodbye")
    assert html == "Hello"


def test_traverse_and_replace_none() -> None:
    html = traverse_and_replace("<p>Hello</p>", lambda e: None)
    assert html == "<p>Hello</p>"


def test_traverse_and_replace_empty() -> None:
    html = traverse_and_replace("<p>Hello</p>", lambda e: "")
    assert html == ""


def test_traverse_and_replace_identity() -> None:
    html = traverse_and_replace("<p>Hello</p>", lambda e: e)
    assert html == "<p>Hello</p>"


def test_traverse_and_replace_fragment() -> None:
    def replace(e):
        if e.tag == "p":
            return "<strong>Goodbye</strong>"
        return e

    html = traverse_and_replace("<p>Hello</p>", replace)
    assert html == "<strong>Goodbye</strong>"


def test_traverse_and_replace_fragments() -> None:
    def replace(e):
        if e.tag == "p":
            return "<strong>Goodbye</strong><strong>Goodbye</strong>"
        return e

    html = traverse_and_replace("<p>Hello</p>", replace)
    assert html == "<strong>Goodbye</strong><strong>Goodbye</strong>"


def traverse_and_replace_nested() -> None:
    def replace(e):
        if e.tag == "strong":
            return "<em>Goodbye</em>"
        return e

    html = traverse_and_replace("<p><strong>Hello</strong></p>", replace)
    assert html == "<p><em>Goodbye</em></p>"


def test_traverse_and_replace_recursive() -> None:
    def replace(e):
        if e.tag == "p":
            return "<strong>Goodbye</strong>"
        elif e.tag == "strong":
            return "<em>Goodbye</em>"
        return e

    html = traverse_and_replace("<p>Hello</p>", replace)
    assert html == "<em>Goodbye</em>"


def test_traverse_and_replace_leading_trailing_text() -> None:
    html = traverse_and_replace("Hello <i>cruel</i> world", lambda e: "beautiful")
    assert html == "Hello beautiful world"
