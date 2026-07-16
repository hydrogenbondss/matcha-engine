from pathlib import Path


class RenPyFormatter:
    """Maps generated images to Ren'Py naming conventions.

    Ren'Py's image auto-definition treats 'sakura happy.png' in game/images
    as `image sakura happy`; we name files `<character>_<pose>.png` and emit
    explicit definitions instead so the mapping is visible and editable.
    """

    def __init__(self, project: Path):
        self.project = Path(project)

    def format_batch(
        self,
        image_paths: list[Path],
        character_name: str,
        poses: list[str],
    ) -> list[tuple[Path, str]]:
        """Pair each image with its target filename inside the project."""
        formatted = []
        for i, path in enumerate(image_paths):
            pose = poses[i] if i < len(poses) else f"pose_{i}"
            formatted.append((path, f"{character_name}_{pose}.png"))
        return formatted

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
        lines.append(f"# --- end matcha: {character_name} ---")
        return "\n".join(lines) + "\n"
