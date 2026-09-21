"""Central configuration for StyleSnap.

All paths are relative to the repository root, making the project portable across
computers. Update these values instead of scattering settings through scripts.
"""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class ProjectConfig:
    """Settings shared by future data, training, evaluation, and app modules."""

    project_name: str = "StyleSnap"

    # Image and reproducibility settings
    image_height: int = 224
    image_width: int = 224
    num_channels: int = 3
    random_seed: int = 42

    # Dataset folders. Class names will be discovered from their subfolders later.
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    train_data_dir: Path = PROJECT_ROOT / "data" / "train"
    validation_data_dir: Path = PROJECT_ROOT / "data" / "validation"
    test_data_dir: Path = PROJECT_ROOT / "data" / "test"

    # Confirmed Phase 2 dataset source and reproducible split policy.
    dataset_id: str = "KrushiJethe/fashion_data"
    dataset_source_split: str = "train"
    train_split: float = 0.70
    validation_split: float = 0.15
    test_split: float = 0.15

    # Saved best model location. This file does not exist until training is run.
    model_path: Path = PROJECT_ROOT / "models" / "stylesnap_mobilenetv2_best.keras"

    # Training settings for the planned two-stage transfer-learning workflow.
    batch_size: int = 32
    stage1_learning_rate: float = 1e-3
    stage2_learning_rate: float = 1e-5
    stage1_epochs: int = 10
    stage2_epochs: int = 10
    fine_tune_layers: int = 30

    # Preprocessing and classification-head settings.
    rotation_factor: float = 0.05
    zoom_height_factor: float = 0.10
    zoom_width_factor: float = 0.10
    horizontal_flip: bool = True
    dropout_rate: float = 0.20

    # Prediction UI setting
    confidence_threshold: float = 0.50

    @property
    def image_size(self) -> tuple[int, int]:
        """Return the (height, width) TensorFlow input shape component."""
        return (self.image_height, self.image_width)

    def validate_split_ratios(self) -> None:
        """Raise an error unless the configured dataset splits total exactly one."""
        total = self.train_split + self.validation_split + self.test_split
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"Dataset split ratios must total 1.0, received {total}.")

    def validate_preprocessing_settings(self) -> None:
        """Validate augmentation and classifier-head settings before they are used."""
        if not 0.0 <= self.rotation_factor <= 1.0:
            raise ValueError("rotation_factor must be between 0.0 and 1.0.")
        if not 0.0 <= self.zoom_height_factor < 1.0:
            raise ValueError("zoom_height_factor must be between 0.0 and 1.0.")
        if not 0.0 <= self.zoom_width_factor < 1.0:
            raise ValueError("zoom_width_factor must be between 0.0 and 1.0.")
        if not 0.0 <= self.dropout_rate < 1.0:
            raise ValueError("dropout_rate must be between 0.0 and 1.0.")


CONFIG = ProjectConfig()
