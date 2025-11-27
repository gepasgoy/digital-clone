class DrugInteractionChecker:
    def __init__(self):
        self.interactions_db = self.load_interactions_database()

    def load_interactions_database(self):
        """Загрузка базы данных взаимодействий"""
        return {
            "warfarin": {
                "aspirin": "Повышение риска кровотечений",
                "ibuprofen": "Повышение риска кровотечений",
                "omeprazole": "Изменение метаболизма",
                "simvastatin": "Повышение концентрации"
            },
            "digoxin": {
                "furosemide": "Гипокалиемия, токсичность дигоксина",
                "hydrochlorothiazide": "Гипокалиемия",
                "verapamil": "Повышение уровня дигоксина"
            },
            "metformin": {
                "contrast_media": "Риск лактат-ацидоза",
                "furosemide": "Изменение концентрации"
            },
            "enalapril": {
                "potassium_supplements": "Гиперкалиемия",
                "spironolactone": "Гиперкалиемия",
                "ibuprofen": "Снижение антигипертензивного эффекта"
            },
            "simvastatin": {
                "clarithromycin": "Риск миопатии",
                "verapamil": "Повышение концентрации"
            }
        }

    def check_interactions(self, drugs):
        """Проверка взаимодействий между препаратами"""
        interactions = []
        drugs_lower = [drug.lower() for drug in drugs]

        for i, drug1 in enumerate(drugs_lower):
            for drug2 in drugs_lower[i + 1:]:
                interaction = self.get_interaction(drug1, drug2)
                if interaction:
                    interactions.append(f"{drug1} + {drug2}: {interaction}")

        return interactions

    def get_interaction(self, drug1, drug2):
        """Получение информации о взаимодействии двух препаратов"""
        return (self.interactions_db.get(drug1, {}).get(drug2) or
                self.interactions_db.get(drug2, {}).get(drug1))

    def get_interaction_severity(self, drug1, drug2):
        """Определение серьезности взаимодействия"""
        severe_interactions = [
            ("warfarin", "aspirin"),
            ("warfarin", "ibuprofen"),
            ("digoxin", "furosemide"),
            ("simvastatin", "clarithromycin")
        ]

        pair = tuple(sorted([drug1.lower(), drug2.lower()]))
        if pair in severe_interactions:
            return "Критическое"
        else:
            return "Умеренное"