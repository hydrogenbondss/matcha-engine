from pathlib import Path
from typing import List, Optional
import shutil


class FilesystemDeployer:
    """Deploy assets to Ren'Py project filesystem."""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.images_dir = self.project_path / "game" / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def deploy_images(
        self,
        image_paths: List[Path],
        subfolder: Optional[str] = None
    ) -> List[Path]:
        """Copy images to Ren'Py project images folder."""
        target_dir = self.images_dir
        if subfolder:
            target_dir = target_dir / subfolder
            target_dir.mkdir(exist_ok=True)
        
        deployed = []
        for img_path in image_paths:
            target = target_dir / img_path.name
            shutil.copy2(img_path, target)
            deployed.append(target)
        
        return deployed
    
    def update_script(
        self,
        character_name: str,
        poses: List[str],
        script_path: Optional[Path] = None
    ) -> str:
        """Append character definitions to Ren'Py script."""
        if script_path is None:
            script_path = self.project_path / "game" / "script.rpy"
        
        definitions = []
        for pose in poses:
            definitions.append(
                f'image {character_name}_{pose} = "{character_name}_{pose}.png"'
            )
        
        definitions.append("")  # blank line
        definitions.append(
            f'# Character: {character_name}'
        )
        definitions.append(
            f'# Poses: {", ".join(poses)}'
        )
        definitions.append("")
        
        block = "\n".join(definitions)
        
        # Append to script
        with open(script_path, "a") as f:
            f.write(f"\n{block}\n")
        
        return block
