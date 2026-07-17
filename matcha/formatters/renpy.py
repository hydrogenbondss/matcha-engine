from pathlib import Path
from typing import Optional


class RenPyFormatter:
    """Maps generated images to Ren'Py naming conventions.

    Ren'Py's image auto-definition treats 'sakura happy.png' in game/images
    as `image sakura happy`; we name files `<character>_<pose>.png` and emit
    explicit definitions instead so the mapping is visible and editable.
    """

    def __init__(self, project: Path):
        self.project = Path(project)

    def resize_for_renpy(
        self,
        image_path: Path,
        max_width: int,
        max_height: int,
    ) -> None:
        """Shrink a sprite in place to fit within max dimensions.

        Aspect ratio is preserved (thumbnail semantics: never upscales).
        720p Ren'Py projects typically want sprites no taller than 720px.
        """
        from PIL import Image

        img = Image.open(image_path)
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        img.save(image_path, "PNG")

    def format_batch(
        self,
        image_paths: list[Path],
        character_name: str,
        poses: list[str],
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
    ) -> list[tuple[Path, str]]:
        """Pair each image with its target filename inside the project,
        optionally resizing to fit the given bounds first."""
        formatted = []
        for i, path in enumerate(image_paths):
            if max_width and max_height:
                self.resize_for_renpy(path, max_width, max_height)
            pose = poses[i] if i < len(poses) else f"pose_{i}"
            formatted.append((path, f"{character_name}_{pose}.png"))
        return formatted

    def generate_show_statement(
        self,
        character_name: str,
        pose: str,
        position: str = "center",
    ) -> str:
        """Ren'Py show statement for pasting into a scene."""
        return f"show {character_name} {pose} at {position}"

    def script_block(self, character_name: str, poses: list[str]) -> str:
        """Ren'Py definitions for the character and its pose images."""
        lines = [
            f"# --- matcha: {character_name} (generated) ---",
            f"define {character_name} = Character(\"{character_name.title()}\")",
        ]
        for pose in poses:
            lines.append(
                f"image {character_name} {pose} = "
                f"\"images/characters/{character_name}_{pose}.png\""
            )
        lines.append("#")
        lines.append(f"# Usage: {self.generate_show_statement(character_name, poses[0])}")
        lines.append(f"# --- end matcha: {character_name} ---")
        return "\n".join(lines) + "\n"
