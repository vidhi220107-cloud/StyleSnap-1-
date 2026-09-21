"""TensorFlow input pipelines for the verified StyleSnap image folders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import tensorflow as tf

from src.config import CONFIG, ProjectConfig


@dataclass(frozen=True)
class DatasetBundle:
    """Prepared datasets plus the class order used by the classifier."""

    train: tf.data.Dataset
    validation: tf.data.Dataset
    test: tf.data.Dataset
    class_names: tuple[str, ...]

    @property
    def num_classes(self) -> int:
        return len(self.class_names)


def build_training_augmentation(config: ProjectConfig = CONFIG) -> tf.keras.Sequential:
    """Create augmentation used exclusively by the training input pipeline."""
    config.validate_preprocessing_settings()
    layers: list[tf.keras.layers.Layer] = []
    if config.horizontal_flip:
        layers.append(tf.keras.layers.RandomFlip("horizontal", seed=config.random_seed))
    layers.extend(
        [
            tf.keras.layers.RandomRotation(config.rotation_factor, seed=config.random_seed),
            tf.keras.layers.RandomZoom(
                height_factor=config.zoom_height_factor,
                width_factor=config.zoom_width_factor,
                seed=config.random_seed,
            ),
        ]
    )
    return tf.keras.Sequential(layers, name="training_augmentation")


def _directory_dataset(path: Path, *, shuffle: bool, config: ProjectConfig) -> tf.data.Dataset:
    """Load one ImageFolder-style split without applying augmentation."""
    if not path.is_dir():
        raise FileNotFoundError(f"Dataset split directory does not exist: {path}")
    return tf.keras.utils.image_dataset_from_directory(
        path,
        labels="inferred",
        label_mode="int",
        color_mode="rgb",
        batch_size=config.batch_size,
        image_size=config.image_size,
        shuffle=shuffle,
        seed=config.random_seed if shuffle else None,
    )


def _class_names(dataset: tf.data.Dataset, split_name: str) -> tuple[str, ...]:
    """Read TensorFlow's alphabetically ordered class mapping for one split."""
    names = getattr(dataset, "class_names", None)
    if not names:
        raise ValueError(f"No class folders were discovered in the {split_name} split.")
    return tuple(names)


def _assert_matching_class_names(
    train_names: tuple[str, ...], validation_names: tuple[str, ...], test_names: tuple[str, ...]
) -> None:
    """Prevent accidental class remapping caused by a changed split folder layout."""
    if validation_names != train_names or test_names != train_names:
        raise ValueError(
            "Class folders differ across train, validation, and test splits. "
            "Recreate the verified Phase 2 splits before training."
        )


def _mobilenet_preprocess(images: tf.Tensor, labels: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
    """Apply the exact MobileNetV2 normalization (pixel range [-1, 1])."""
    return tf.keras.applications.mobilenet_v2.preprocess_input(images), labels


def _prepare_dataset(
    dataset: tf.data.Dataset,
    *,
    augment: bool,
    config: ProjectConfig,
) -> tf.data.Dataset:
    """Apply optional training augmentation, MobileNetV2 preprocessing, and prefetching."""
    if augment:
        augmentation = build_training_augmentation(config)
        dataset = dataset.map(
            lambda images, labels: (augmentation(images, training=True), labels),
            num_parallel_calls=tf.data.AUTOTUNE,
        )
    return dataset.map(
        _mobilenet_preprocess,
        num_parallel_calls=tf.data.AUTOTUNE,
        deterministic=not augment,
    ).prefetch(tf.data.AUTOTUNE)


def load_datasets(config: ProjectConfig = CONFIG) -> DatasetBundle:
    """Load the fixed dataset splits with augmentation limited to training images."""
    config.validate_preprocessing_settings()
    train_raw = _directory_dataset(config.train_data_dir, shuffle=True, config=config)
    validation_raw = _directory_dataset(config.validation_data_dir, shuffle=False, config=config)
    test_raw = _directory_dataset(config.test_data_dir, shuffle=False, config=config)

    class_names = _class_names(train_raw, "train")
    _assert_matching_class_names(
        class_names,
        _class_names(validation_raw, "validation"),
        _class_names(test_raw, "test"),
    )
    return DatasetBundle(
        train=_prepare_dataset(train_raw, augment=True, config=config),
        validation=_prepare_dataset(validation_raw, augment=False, config=config),
        test=_prepare_dataset(test_raw, augment=False, config=config),
        class_names=class_names,
    )
