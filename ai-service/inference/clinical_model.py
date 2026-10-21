import joblib

class ClinicalModel:
    def __init__(self, path):
        self.obj = joblib.load(path)
        self.model = self.obj["model"]
        self.version = self.obj.get("version", "clinical-model")
        self.feature_names = self.obj.get("feature_names")

    def predict(self, data):
        if self.feature_names:
            row = {}
            aliases = {
                "Age":"age", "Gender":"gender", "Tobacco Use":"tobaccoUse",
                "Alcohol Consumption":"alcohol", "HPV Infection":"hpvInfection",
                "Betel Quid Use":"betelQuid", "Chronic Sun Exposure":"chronicSunExposure",
                "Poor Oral Hygiene":"poorOralHygiene",
                "Diet (Fruits & Vegetables Intake)":"dietFruitsVegetables",
                "Family History of Cancer":"familyHistoryOfCancer",
                "Compromised Immune System":"compromisedImmuneSystem",
                "Oral Lesions":"oralLesions", "Unexplained Bleeding":"unexplainedBleeding",
                "Difficulty Swallowing":"difficultySwallowing",
                "White or Red Patches in Mouth":"whiteOrRedPatches",
                "Early Diagnosis":"earlyDiagnosis"
            }
            for feature in self.feature_names:
                key = aliases.get(feature, feature)
                value = data.get(key, data.get(feature, None)) if hasattr(data, "get") else None
                if value in (None, "", "unknown"):
                    value = None if feature == "Age" else "Unknown"
                if feature == "Age":
                    try: value = float(value) if value is not None else None
                    except (TypeError, ValueError): value = None
                else:
                    value = str(value).strip().title()
                row[feature] = value
            import pandas as pd
            X = pd.DataFrame([row], columns=self.feature_names)
            probs = self.model.predict_proba(X)[0]
            classes = list(self.model.classes_)
            pos_index = classes.index(1) if 1 in classes else int(probs.argmax())
            confidence = float(probs[pos_index])
            return ("elevated" if confidence >= 0.5 else "lower"), confidence, self.version
        # Backward compatibility for old demo artifacts
        def get(k, default="unknown"):
            v = data.get(k, default) if hasattr(data, "get") else default
            return v[0] if isinstance(v, list) else v
        def enc(v): return {"no":0,"unknown":0,"occasionally":1,"yes":2}.get(str(v).lower(),0)
        x=[[float(get("age",0) or 0),enc(get("smoking")),enc(get("betelQuid")),enc(get("alcohol"))]]
        p=self.model.predict_proba(x)[0]; i=int(p.argmax())
        return self.model.classes_[i], float(p[i]), self.version
