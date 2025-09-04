import datetime

class HistoryLog:
    def __init__(self):
        self.logs = []

    def log(self, user, query, result):
        timestamp = datetime.datetime.utcnow().isoformat()
        self.logs.append({"user": user, "query": query, "result": result, "timestamp": timestamp})
