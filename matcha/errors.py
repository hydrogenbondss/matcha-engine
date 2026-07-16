class MatchaError(Exception):
    """Base class for all Matcha pipeline errors."""


class PreflightError(MatchaError):
    """Raised before any generation when the environment can't succeed
    (server unreachable, unknown checkpoint/LoRA, suspicious model file)."""


class GenerationError(MatchaError):
    """Raised when ComfyUI reports an execution error for a queued prompt.

    Carries the server's node-level failure so the user sees the real cause
    (e.g. 'Error while deserializing header' from a corrupt checkpoint)
    instead of a silent 'Generated 0 images'.
    """

    def __init__(self, message: str, node_type: str = "", prompt_id: str = ""):
        self.node_type = node_type
        self.prompt_id = prompt_id
        super().__init__(message)
