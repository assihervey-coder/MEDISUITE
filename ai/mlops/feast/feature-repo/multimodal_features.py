"""Définitions de features Feast pour la fusion multimodale."""
from datetime import timedelta

from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

patient = Entity(name="patient_id", join_keys=["patient_id"])

biologie = FileSource(
    path="ai/datasets/processed/biologie.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)

fv_biologie = FeatureView(
    name="biologie_recente",
    entities=[patient],
    ttl=timedelta(days=7),
    schema=[Field(name="hba1c", dtype=Float32),
            Field(name="creatinine_mgdl", dtype=Float32),
            Field(name="hemoglobine", dtype=Float32),
            Field(name="nb_hospitalisations", dtype=Int64)],
    source=biologie,
    online=True,
)
