"""
test_evaluate_shap.py

Unit tests for quantitative SHAP evaluation pipeline in SPARK.
Verifies held-out data splitting, gradient saliency computation, and figure generation.
"""

from pathlib import Path

import numpy as np
import pytest
import tensorflow as tf

from training.evaluate_shap import (
    IMU_CHANNELS,
    compute_gradient_saliency_batch,
    evaluate_held_out_shap,
)


@pytest.fixture
def mock_cnn_model(tmp_path: Path) -> Path:
    """Create a minimal synthetic 1D CNN matching SPARK output shape for fast testing."""
    inputs = tf.keras.Input(shape=(200, 6))
    x = tf.keras.layers.Conv1D(8, kernel_size=3, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    outputs = tf.keras.layers.Dense(2, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    model_path = tmp_path / "mock_spark_cnn.keras"
    model.save(model_path)
    return model_path


def test_compute_gradient_saliency_shape():
    inputs = tf.keras.Input(shape=(200, 6))
    x = tf.keras.layers.GlobalAveragePooling1D()(inputs)
    outputs = tf.keras.layers.Dense(2, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    batch = np.random.randn(4, 200, 6).astype(np.float32)
    saliency = compute_gradient_saliency_batch(model, batch)

    assert saliency.shape == (4, 200, 6)
    assert not np.isnan(saliency).any()


def test_evaluate_held_out_shap_execution(tmp_path: Path):
    data_dir = Path("data/processed_sisfall")
    model_path = Path("data/processed_sisfall/model/spark_cnn.keras")

    if not data_dir.exists() or not model_path.exists():
        pytest.skip("SisFall processed dataset or model not present in local repo")

    out_dir = tmp_path / "figures"
    metrics = evaluate_held_out_shap(
        data_dir=data_dir,
        model_path=model_path,
        out_dir=out_dir,
        n_samples=15,  # small batch for fast unit test
        seed=42,
    )

    assert "channel_metrics" in metrics
    assert set(metrics["channel_metrics"].keys()) == set(IMU_CHANNELS)
    assert "temporal_phase_metrics" in metrics
    assert "pre_impact_pct" in metrics["temporal_phase_metrics"]

    # Verify figures were exported
    assert (out_dir / "fig_shap_channel_attribution.pdf").exists()
    assert (out_dir / "fig_shap_channel_attribution.png").exists()
    assert (out_dir / "fig_shap_temporal_saliency.pdf").exists()
    assert (out_dir / "fig_shap_temporal_saliency.png").exists()
    assert (out_dir / "fig_shap_fall_vs_adl_contrast.pdf").exists()
    assert (out_dir / "fig_shap_fall_vs_adl_contrast.png").exists()
    assert (out_dir / "shap_attribution_metrics.json").exists()
