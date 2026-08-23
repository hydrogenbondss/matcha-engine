import re
import shutil
from pathlib import Path


class FilesystemDeployer:
    """Copies images into a Ren'Py project and maintains a matcha .rpy file."""

    def __init__(self, project: Path):
        self.project = Path(project)
        self.images_dir = self.project / "game" / "images"
        self.script_path = self.project / "game" / "matcha_characters.rpy"

    def deploy_images(
        self,
        formatted: list[tuple[Path, str]],
        subfolder: str = "characters",
    ) -> list[Path]:
        target_dir = self.images_dir / subfolder if subfolder else self.images_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        deployed = []
        for src, filename in formatted:
            dest = target_dir / filename
            shutil.copyfile(src, dest)
            deployed.append(dest)
        return deployed

    def update_script(self, character_name: str, script_block: str) -> Path:
        """Write/replace this character's block in matcha_characters.rpy.

        Definitions live in a dedicated generated file rather than script.rpy
        so re-runs are idempotent and never touch hand-written game code.
        """
        existing = ""
        if self.script_path.exists():
            existing = self.script_path.read_text()

        start = f"# --- matcha: {character_name} (generated) ---"
        end = f"# --- end matcha: {character_name} ---"
        pattern = re.compile(
            re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.DOTALL
        )
        existing = pattern.sub("", existing)

        content = existing.rstrip()
        if content:
            content += "\n\n"
        content += script_block
        self.script_path.parent.mkdir(parents=True, exist_ok=True)
        self.script_path.write_text(content)
        return self.script_path
