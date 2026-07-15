from pathlib import Path
from typing import List
from PIL import Image


class RenPyFormatter:
    """Format and resize images for Ren'Py deployment."""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.images_dir = self.project_path / "game" / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def resize_for_renpy(
        self,
        image_path: Path,
        width: int = 1280,
        height: int = 720,
        maintain_aspect: bool = True
    ) -> Image.Image:
        """Resize image to Ren'Py standard resolution."""
        img = Image.open(image_path)
        
        if maintain_aspect:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        return img
    
    def save_character_sprite(
        self,
        image: Image.Image,
        character_name: str,
        pose: str,
        suffix: str = ".png"
    ) -> Path:
        """Save character sprite with Ren'Py naming convention."""
        filename = f"{character_name}_{pose}{suffix}"
        output_path = self.images_dir / filename
        image.save(output_path, "PNG")
        return output_path
    
    def generate_show_statement(
        self,
        character_name: str,
        pose: str,
        position: str = "center"
    ) -> str:
        """Generate Ren'Py show statement for a character."""
        return f'show {character_name}_{pose} at {position}'
    
    def format_batch(
        self,
        image_paths: List[Path],
        character_name: str,
        poses: List[str],
        width: int = 1280,
        height: int = 720
    ) -> List[Path]:
        """Format a batch of images for Ren'Py."""
        output_paths = []
        
        for img_path, pose in zip(image_paths, poses):
            resized = self.resize_for_renpy(img_path, width, height)
            out_path = self.save_character_sprite(resized, character_name, pose)
            output_paths.append(out_path)
        
        return output_paths
