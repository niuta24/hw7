from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


def check_for_alerts(text: str):
    alert_triggered = False
    reason = ""

    if "password" in text.lower():
        alert_triggered = True
        reason = "Contains 'password'"
    elif re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
        alert_triggered = True
        reason = "Possible SSN pattern"

    if alert_triggered:
        filename = f"error_reports/alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"Content: {text}\n")
        logger.warning(f"Alert triggered: {reason} -- Report saved to {filename}")
