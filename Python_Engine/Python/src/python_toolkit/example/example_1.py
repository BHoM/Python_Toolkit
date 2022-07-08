import argparse

from ..bhom.bhom_analytics import bhom_analytics


@bhom_analytics
def example_1(a: float = 23, b: int = 42) -> str:
    """An example method that generates and returns some text.
    This method is also decorated with a ToBHoM method, which
    pushes its output into a JSON for use in downstream BHoM
    operations.

    Arguments:
        a (float, optional): The first number. Default is 23.
        b (int, optional): The second number. Default is 42.

    Returns:
        string: Some really interesting text.

    """

    return f"Hello there! You entered {a} and {b}.\n\nWhen added those equal {a + b}. Isn't that nice. Give yourself a pat on the back for such an excellent job.\n\nMaybe go make a nice cup of tea (or coffee, I'm not here to dictate your beverage choice).\n\nI've always been partial to an Irish Breakfast blend, though Assam is a close second.\n\nEither way, after all that hard work you're probably thirsty, so relax, put your feet up and take a break.\n\nYou could even go outside, or watch a movie. You could read a book.\n\nA sci-fi book, or a tragedy perhaps.\n\nDid you ever hear the tragedy of Darth Plagueis The Wise? I thought not. It's not a story the Jedi would tell you. It's a Sith legend. Darth Plagueis was a Dark Lord of the Sith, so powerful and so wise he could use the Force to influence the midichlorians to create life… He had such a knowledge of the dark side that he could even keep the ones he cared about from dying. The dark side of the Force is a pathway to many abilities some consider to be unnatural. He became so powerful… the only thing he was afraid of was losing his power, which eventually, of course, he did. Unfortunately, he taught his apprentice everything he knew, then his apprentice killed him in his sleep. Ironic. He could save others from death, but not himself."


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", required=False, help="A float value", type=float, default=23
    )
    parser.add_argument(
        "-b", required=False, help="Another int value", type=int, default=42
    )
    args = parser.parse_args()

    example_1(args.a, args.b)
