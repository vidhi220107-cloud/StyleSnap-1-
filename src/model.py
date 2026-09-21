"""MobileNetV2 transfer-learning model construction for StyleSnap."""

from __future__ import annotations

import tensorflow as tf

from src.config import CONFIG, ProjectConfig


def build_mobilenetv2_classifier(
    num_classes: int,
    config: ProjectConfig = CONFIG,
) -> tf.keras.Model:
    """Build the frozen-backbone classifier for Stage 1 training.

    ``num_classes`` must come from the actual training folders via
    ``preprocessing.load_datasets()``, never from a manually maintained list.
    Calling this function may download ImageNet weights if they are not already
    cached; Phase 3 only defines this reusable function and does not call it.
    """
    if num_classes < 2:
        raise ValueError("StyleSnap requires at least two discovered classes.")
    config.validate_preprocessing_settings()

    inputs = tf.keras.Input(
        shape=(config.image_height, config.image_width, config.num_channels),
        name="image",
    )
    backbone = tf.keras.applications.MobileNetV2(
        input_shape=(config.image_height, config.image_width, config.num_channels),
        include_top=False,
        weights="imagenet",
    )
    backbone.trainable = False

    features = backbone(inputs, training=False)
    features = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling")(features)
    features = tf.keras.layers.Dropout(config.dropout_rate, name="dropout")(features)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="predictions")(features)
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="stylesnap_mobilenetv2")

    # Retain a direct reference for the later fine-tuning stage without unfreezing it now.
    model.backbone = backbone
    return model
