from pathlib import Path
from typing import Optional


class RenPyFormatter:
    """Maps generated images to Ren'Py naming conventions.

    Ren'Py's image auto-definition treats 'sakura happy.png' in game/images
    as `image sakura happy`; we name files `<character>_<pose>.png` and emit
    explicit definitions instead so the mapping is visible and editable.
    """

    # Convention: full sprites → images/characters/<name>_<pose>.png
    # Side portraits → images/characters/<name>_<pose>_side.png
    SIDE_SUFFIX = "_side"

    def __init__(self, project: Path):
        self.project = Path(project)

    @staticmethod
    def side_filename(character_name: str, pose: str) -> str:
        return f"{character_name}_{pose}{RenPyFormatter.SIDE_SUFFIX}.png"

    @staticmethod
    def side_image_path(character_name: str, pose: str) -> str:
        return (
            f"images/characters/"
            f"{RenPyFormatter.side_filename(character_name, pose)}"
        )

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

    def crop_side_portrait(
        self,
        image_path: Path,
        dest_path: Path,
        height_ratio: float = 0.45,
    ) -> Path:
        """Write a head/shoulders portrait cropped from the top of a sprite.

        Deterministic top-center crop: keep the full width and the top
        ``height_ratio`` fraction of the height. Suited to waist-up VN
        sprites where the face sits in the upper portion of the frame.
        """
        from PIL import Image

        if not 0.0 < height_ratio <= 1.0:
            raise ValueError(
                f"height_ratio must be in (0, 1], got {height_ratio}"
            )

        img = Image.open(image_path)
        w, h = img.size
        crop_h = max(1, int(round(h * height_ratio)))
        portrait = img.crop((0, 0, w, crop_h))
        dest_path = Path(dest_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        portrait.save(dest_path, "PNG")
        return dest_path

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

    def format_side_images(
        self,
        image_paths: list[Path],
        character_name: str,
        poses: list[str],
        height_ratio: float = 0.45,
        dest_dir: Optional[Path] = None,
    ) -> list[tuple[Path, str]]:
        """Crop side portraits from full sprites and pair with deploy filenames.

        ``image_paths`` should already be resized (same sources as format_batch).
        Crops are written beside each source (or into ``dest_dir``) as
        ``<name>_<pose>_side.png``.
        """
        formatted = []
        for i, path in enumerate(image_paths):
            pose = poses[i] if i < len(poses) else f"pose_{i}"
            filename = self.side_filename(character_name, pose)
            out = (Path(dest_dir) / filename) if dest_dir else path.with_name(filename)
            self.crop_side_portrait(path, out, height_ratio=height_ratio)
            formatted.append((out, filename))
        return formatted

    def generate_show_statement(
        self,
        character_name: str,
        pose: str,
        position: str = "center",
    ) -> str:
        """Ren'Py show statement for pasting into a scene."""
        return f"show {character_name} {pose} at {position}"

    def script_block(
        self,
        character_name: str,
        poses: list[str],
        *,
        display_name: Optional[str] = None,
        color: Optional[str] = None,
        layered: bool = False,
        side_image: bool = False,
    ) -> str:
        """Ren'Py definitions for the character and its pose images.

        Defaults reproduce the flat `image <char> <pose>` layout. Options add
        the deploy "last mile" that raw generation tools don't:
          - ``layered``: emit a ``layeredimage`` grouping poses as attributes so
            ``show <char> <pose>`` composes from one declared sprite set.
          - ``side_image``: emit ``image side <char> <pose>`` definitions pointing
            at cropped portrait PNGs and wire ``Character(image=...)`` so
            portraits auto-show beside dialogue.
          - ``display_name`` / ``color``: a richer ``Character`` definition.
        """
        display = display_name or character_name.title()
        char_args = [f'"{display}"']
        if color:
            char_args.append(f'color="{color}"')
        if side_image:
            char_args.append(f'image="{character_name}"')

        lines = [
            f"# --- matcha: {character_name} (generated) ---",
            f"define {character_name} = Character({', '.join(char_args)})",
        ]

        if layered:
            lines.append(f"layeredimage {character_name}:")
            lines.append("    group pose:")
            for i, pose in enumerate(poses):
                default = " default" if i == 0 else ""
                lines.append(
                    f"        attribute {pose}{default} "
                    f"\"images/characters/{character_name}_{pose}.png\""
                )
        else:
            for pose in poses:
                lines.append(
                    f"image {character_name} {pose} = "
                    f"\"images/characters/{character_name}_{pose}.png\""
                )

        if side_image:
            lines.append("#")
            lines.append(
                "# Side images: cropped head/shoulders portraits "
                "(not full sprites)."
            )
            for pose in poses:
                lines.append(
                    f"image side {character_name} {pose} = "
                    f"\"{self.side_image_path(character_name, pose)}\""
                )

        lines.append("#")
        lines.append(f"# Usage: {self.generate_show_statement(character_name, poses[0])}")
        lines.append(f"# --- end matcha: {character_name} ---")
        return "\n".join(lines) + "\n"
