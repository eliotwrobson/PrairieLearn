from enum import Enum
from typing import Callable, List, Optional, Tuple
from typing_extensions import assert_never
import prairielearn as pl
import lxml.html
from html import escape
import sympy
import chevron
import math
import big_o_utils as bou

VARIABLES_DEFAULT = ''
DISPLAY_DEFAULT = 'inline'
SIZE_DEFAULT = 35
PLACEHOLDER_TEXT_THRESHOLD = 20
SHOW_HELP_TEXT_DEFAULT = True
WEIGHT_DEFAULT = 1


class BigOType(Enum):
    BIGO = r'O'
    THETA = r'\Theta'
    OMEGA = r'\Omega'
    LITTLE_O = r'o'
    LITTLE_OMEGA = r'\omega'


class DisplayType(Enum):
    INLINE = 'inline'
    BLOCK = 'block'


def prepare(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)
    required_attribs = ['answers-name']
    optional_attribs = ['weight', 'correct-answer', 'variables', 'size', 'display', 'show-help-text', 'type']
    pl.check_attribs(element, required_attribs, optional_attribs)
    name = pl.get_string_attrib(element, 'answers-name')

    if pl.has_attrib(element, 'correct-answer'):
        if name in data['correct_answers']:
            raise ValueError(f'duplicate correct_answers variable name: {name}')
        data['correct_answers'][name] = pl.get_string_attrib(element, 'correct-answer')


def render(element_html: str, data: pl.QuestionData) -> str:
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, 'answers-name')
    variables = get_variables_list(pl.get_string_attrib(element, 'variables', VARIABLES_DEFAULT))
    if len(variables) > 1:
        raise ValueError('Only one variable is supported')
    display = DisplayType(pl.get_string_attrib(element, 'display', DISPLAY_DEFAULT))
    size = pl.get_integer_attrib(element, 'size', SIZE_DEFAULT)

    bigo_type_name = pl.get_string_attrib(element, 'type', BigOType.BIGO.name).upper()
    bigo_type = BigOType[bigo_type_name].value

    operators: List[str] = ['exp', 'log', 'sqrt', 'factorial', '( )', '+', '-', '*', '/', '^', '**']
    constants: List[str] = ['pi', 'e']

    info_params = {
        'format': True,
        'variables': variables,
        'operators': operators,
        'constants': constants
    }

    PARTIAL_SCORE_DEFAULT: pl.PartialScore = {'score': None}
    score = data['partial_scores'].get(name, PARTIAL_SCORE_DEFAULT).get('score')

    if data['panel'] == 'question':
        editable = data['editable']
        raw_submitted_answer = data['raw_submitted_answers'].get(name)

        with open('pl-big-o-input.mustache', 'r', encoding='utf-8') as f:
            info = chevron.render(f, info_params).strip()

        if raw_submitted_answer is not None:
            raw_submitted_answer = escape(raw_submitted_answer)

        score_type, score_value = determine_score_params(score)

        html_params = {
            'question': True,
            'name': name,
            'editable': editable,
            'info': info,
            'size': size,
            'show_info': pl.get_boolean_attrib(element, 'show-help-text', SHOW_HELP_TEXT_DEFAULT),
            'uuid': pl.get_uuid(),
            display.value: True,
            'show_placeholder': size >= PLACEHOLDER_TEXT_THRESHOLD,
            'raw_submitted_answer': raw_submitted_answer,
            'type': bigo_type,
            score_type: True,
            'score_value': score_value
        }

        with open('pl-big-o-input.mustache', 'r', encoding='utf-8') as f:
            return chevron.render(f, html_params).strip()

    elif data['panel'] == 'submission':
        parse_error: Optional[str] = data['format_errors'].get(name)
        missing_input = False
        feedback = None
        a_sub = None
        raw_submitted_answer = None

        if parse_error is None and name in data['submitted_answers']:
            a_sub = sympy.latex(sympy.sympify(data['submitted_answers'][name], evaluate=False))
            if name in data['partial_scores']:
                feedback = data['partial_scores'][name].get('feedback')
        elif name not in data['submitted_answers']:
            missing_input = True
            parse_error = None
        else:

            # Use the existing format text in the invalid popup.
            with open('pl-big-o-input.mustache', 'r', encoding='utf-8') as f:
                info = chevron.render(f, info_params).strip()

            # Render invalid popup
            raw_submitted_answer = data['raw_submitted_answers'].get(name)
            if isinstance(parse_error, str):
                with open('pl-big-o-input.mustache', 'r', encoding='utf-8') as f:
                    parse_error += chevron.render(f, {'format_error': True, 'format_string': info}).strip()
            if raw_submitted_answer is not None:
                raw_submitted_answer = pl.escape_unicode_string(raw_submitted_answer)

        score_type, score_value = determine_score_params(score)

        html_params = {
            'submission': True,
            'type': bigo_type,
            'parse_error': parse_error,
            'uuid': pl.get_uuid(),
            display.value: True,
            'error': parse_error or missing_input,
            'a_sub': a_sub,
            'feedback': feedback,
            'raw_submitted_answer': raw_submitted_answer,
            score_type: True,
            'score_value': score_value
        }
        with open('pl-big-o-input.mustache', 'r', encoding='utf-8') as f:
            return chevron.render(f, html_params).strip()

    # Display the correct answer.
    elif data['panel'] == 'answer':
        a_tru = data['correct_answers'].get(name)
        if a_tru is not None:
            a_tru = sympy.sympify(a_tru)
            html_params = {
                'answer': True,
                'a_tru': sympy.latex(a_tru),
                'type': bigo_type
            }
            with open('pl-big-o-input.mustache', 'r', encoding='utf-8') as f:
                return chevron.render(f, html_params).strip()
        return ''

    assert_never(data['panel'])


def parse(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, 'answers-name')
    variables = get_variables_list(pl.get_string_attrib(element, 'variables', VARIABLES_DEFAULT))

    a_sub = data['submitted_answers'].get(name)
    if not a_sub:
        data['format_errors'][name] = 'No submitted answer.'
        data['submitted_answers'][name] = None
        return

    # Replace '^' with '**' wherever it appears.
    a_sub = a_sub.replace('^', '**')

    # Replace unicode minus with hyphen minus wherever it occurs
    a_sub = a_sub.replace(u'\u2212', '-')

    # Strip whitespace
    a_sub = a_sub.strip()
    data['submitted_answers'][name] = a_sub

    s = None
    try:
        bou.convert_string_to_sympy(a_sub, variables)
    except bou.HasFloatError as err:
        s = f'Your answer contains the floating-point number {err.n}. ' \
            f'All numbers must be expressed as integers (or ratios of integers)' \
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except bou.HasInvalidExpressionError as err:
        s = f'Your answer has an invalid expression. '\
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except bou.HasInvalidFunctionError as err:
        s = f'Your answer calls an invalid function "{err.text}". ' \
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except bou.HasInvalidVariableError as err:
        s = f'Your answer refers to an invalid variable "{err.text}". ' \
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except bou.HasParseError as err:
        s = f'Your answer has a syntax error. ' \
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except bou.HasEscapeError as err:
        s = f'Your answer must not contain the character "\\". ' \
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except bou.HasCommentError as err:
        s = f'Your answer must not contain the character "#". ' \
            f'<br><br><pre>{bou.point_to_error(a_sub, err.offset)}</pre>'
    except Exception:
        s = 'Invalid format.'
    finally:
        if (s is not None):
            data['format_errors'][name] = s
            data['submitted_answers'][name] = None


def grade(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, 'answers-name')
    variables = get_variables_list(pl.get_string_attrib(element, 'variables', VARIABLES_DEFAULT))
    weight = pl.get_integer_attrib(element, 'weight', WEIGHT_DEFAULT)
    a_tru: str = data['correct_answers'].get(name, '')

    def get_grade_fn(grade_fn: bou.BigoGradingFunctionT) -> Callable[[str], Tuple[float, str]]:
        def grade(a_sub: str) -> Tuple[float, str]:
            return grade_fn(a_tru, a_sub, variables)
        return grade

    bigo_type_name = pl.get_string_attrib(element, 'type', BigOType.BIGO.name).upper()
    bigo_type = BigOType[bigo_type_name]

    if bigo_type is BigOType.BIGO:
        pl.grade_question_parameterized(data, name, get_grade_fn(bou.grade_bigo_expression), weight=weight)
    elif bigo_type is BigOType.THETA:
        pl.grade_question_parameterized(data, name, get_grade_fn(bou.grade_theta_expression), weight=weight)
    elif bigo_type is BigOType.OMEGA:
        pl.grade_question_parameterized(data, name, get_grade_fn(bou.grade_omega_expression), weight=weight)
    elif bigo_type is BigOType.LITTLE_O:
        pl.grade_question_parameterized(data, name, get_grade_fn(bou.grade_little_o_expression), weight=weight)
    elif bigo_type is BigOType.LITTLE_OMEGA:
        pl.grade_question_parameterized(data, name, get_grade_fn(bou.grade_little_omega_expression), weight=weight)
    else:
        assert_never(bigo_type)


def get_variables_list(variables_string: str) -> List[str]:
    variables_list = [variable.strip() for variable in variables_string.split(',')]
    if variables_list == ['']:
        return []
    return variables_list


def determine_score_params(score: Optional[float]) -> Tuple[str, float]:
    if score is not None:
        try:
            score_val: float = float(score)
            if score_val >= 1:
                return ('correct', 1.0)
            elif score_val > 0:
                return ('partial', math.floor(score_val * 100))
            else:
                return ('incorrect', 0.0)
        except Exception:
            raise ValueError(f'invalid score {score}')
    else:
        return '', 0.0
