"""Two-stage MobileNetV2 training script for StyleSnap."""

from __future__ import annotations

import tensorflow as tf

from src.config import CONFIG
from src.preprocessing import load_datasets
from src.model import build_mobilenetv2_classifier


def main() -> None:
    print("Loading prepared dataset...")
    bundle = load_datasets()

    print(f"Classes: {bundle.num_classes}")
    print(f"Class names: {bundle.class_names}")

    print("\nBuilding MobileNetV2 model...")
    model = build_mobilenetv2_classifier(
        num_classes=bundle.num_classes,
        config=CONFIG,
    )

    checkpoint = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(CONFIG.model_path),
        monitor="val_accuracy",
        save_best_only=True,
        mode="max",
        verbose=1,
    )

    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=3,
        mode="max",
        restore_best_weights=True,
        verbose=1,
    )

    # ---------------------------------------------------------
    # Stage 1: Train classification head with frozen backbone
    # ---------------------------------------------------------
    print("\n===== STAGE 1: FROZEN BACKBONE =====")

    model.backbone.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=CONFIG.stage1_learning_rate
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        bundle.train,
        validation_data=bundle.validation,
        epochs=CONFIG.stage1_epochs,
        callbacks=[checkpoint, early_stopping],
    )

    # ---------------------------------------------------------
    # Stage 2: Fine-tune the last configured backbone layers
    # ---------------------------------------------------------
    print("\n===== STAGE 2: FINE-TUNING =====")

    model.backbone.trainable = True

    for layer in model.backbone.layers[:-CONFIG.fine_tune_layers]:
        layer.trainable = False

    for layer in model.backbone.layers[-CONFIG.fine_tune_layers:]:
        layer.trainable = True

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=CONFIG.stage2_learning_rate
        ),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        bundle.train,
        validation_data=bundle.validation,
        epochs=CONFIG.stage2_epochs,
        callbacks=[checkpoint, early_stopping],
    )

    # ---------------------------------------------------------
    # Final evaluation
    # ---------------------------------------------------------
    print("\n===== FINAL TEST EVALUATION =====")

    best_model = tf.keras.models.load_model(CONFIG.model_path)

    test_loss, test_accuracy = best_model.evaluate(
        bundle.test,
        verbose=1,
    )

    print(f"\nTest loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"\nBest model saved to: {CONFIG.model_path}")


if __name__ == "__main__":
    main()