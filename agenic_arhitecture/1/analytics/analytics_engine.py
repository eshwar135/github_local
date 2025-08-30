# File: analytics_engine.py

class AnalyticsEngine:
    def __init__(self):
        self.metrics = {}

    def update_metrics(self, case_type, status):
        # Update summary metrics based on automation case outcomes
        if case_type not in self.metrics:
            self.metrics[case_type] = {'total': 0, 'success': 0, 'failure': 0}
        self.metrics[case_type]['total'] += 1
        if status == "success":
            self.metrics[case_type]['success'] += 1
        elif status == "failure":
            self.metrics[case_type]['failure'] += 1

    def get_summary(self):
        # Return overall summary-level metrics as a report string
        report = "Summary Metrics:\n"
        for case_type, data in self.metrics.items():
            report += (f"- {case_type.capitalize()}: Total={data['total']}, "
                       f"Success={data['success']}, Failure={data['failure']}\n")
        return report

    def get_detailed_analysis(self, case_type):
        # Return details for a specific automation case type
        if case_type in self.metrics:
            data = self.metrics[case_type]
            return (f"Detail for {case_type}:\n"
                    f"Total: {data['total']}\n"
                    f"Success: {data['success']}\n"
                    f"Failure: {data['failure']}")
        return f"No data for {case_type}."
