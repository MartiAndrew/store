from prometheus_client import CollectorRegistry, Counter

registry = CollectorRegistry()


db_pool_timeout_errors_count = Counter(
    "db_pool_timeout_errors_count",
    "Number of pool connection errors.",
    registry=registry,
)
