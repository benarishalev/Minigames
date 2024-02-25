from random import choice, randint


def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'you Silent..'
    elif lowered == 'game':
        return '<- Ok Ill send it ->'
