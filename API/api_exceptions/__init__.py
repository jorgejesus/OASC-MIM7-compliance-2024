# Exceptions to be reported by API

# This exception is mainly for /r1
class ComplianceException(Exception):
    def __init__(self, service_url: str, status: str, details: str):
        self.service_url = service_url
        self.status = status
        self.details = details
