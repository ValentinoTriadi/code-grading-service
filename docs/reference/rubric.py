class MetricData:
    def __init__(self, aspect: str, weight: float, description: str):
        self.aspect = aspect
        self.weight = weight
        self.description = description

base_metrics = [
    MetricData(
        aspect="Correctness",
        weight=0.4,
        description="Functionality, edge cases, syntax, and logic implementation",
    ),
    MetricData(
        aspect="Efficiency",
        weight=0.27,
        description="Time/space complexity and optimal algorithms usage",
    ),
    MetricData(
        aspect="Data Structures",
        weight=0.15,
        description="Appropriate selection and usage of data structures",
    ),
    MetricData(
        aspect="Code Quality",
        weight=0.1,
        description="Readability, documentation, and code structure",
    ),
    MetricData(
        aspect="Testing",
        weight=0.08,
        description="Test design, debugging, and error handling",
    ),
]