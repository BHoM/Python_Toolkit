"""Here be dragons!"""

from pathlib import Path

from ..bhom.analytics import bhom_analytics


@bhom_analytics()
def nuke_directory(pth: Path) -> None:
    """Delete a directory and all its contents. Please be careful with this method!

    Args:
        pth (Path):
            The directory to delete

    Returns:
        None
    """
    for child in pth.iterdir():
        if child.is_file():
            child.unlink()
        else:
            nuke_directory(child)
    pth.rmdir()
