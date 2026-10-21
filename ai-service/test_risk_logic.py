from app import derive_risk_and_classification


def test_cancer_is_high_risk():
    risk, classification = derive_risk_and_classification(
        "cancer",
        {"cancer": 0.91, "opmd": 0.04, "no_lesion": 0.02, "normal_anatomic_variant": 0.01, "benign": 0.01, "developmental_anomaly": 0.01},
        0.91,
    )
    assert risk == "high"
    assert classification == "high_risk"


def test_no_lesion_is_safe():
    risk, classification = derive_risk_and_classification(
        "no_lesion",
        {"cancer": 0.01, "opmd": 0.02, "no_lesion": 0.82, "normal_anatomic_variant": 0.10, "benign": 0.05, "developmental_anomaly": 0.00},
        0.82,
    )
    assert risk == "low"
    assert classification == "safe"


def test_opmd_is_medium_risk():
    risk, classification = derive_risk_and_classification(
        "opmd",
        {"cancer": 0.03, "opmd": 0.62, "no_lesion": 0.08, "normal_anatomic_variant": 0.04, "benign": 0.13, "developmental_anomaly": 0.10},
        0.62,
    )
    assert risk == "medium"
    assert classification == "medium_risk"
