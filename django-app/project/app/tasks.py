from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from .services import process_and_store_logs, AlertService
from .models import ThreatLog
from .ai_analyzer import analyze_log
import logging

logger = logging.getLogger(__name__)


def _risk_from_severity(severity):
    return {"LOW": 15, "MEDIUM": 40, "HIGH": 70, "CRITICAL": 90}.get(severity, 15)


def _rank(severity):
    return {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}.get(severity, 0)


def process_ai_analysis():
    """Enrich recent rule-processed logs using local Ollama."""
    candidates = ThreatLog.objects.filter(ai_analyzed=False).order_by('timestamp')[:50]
    alert_service = AlertService()

    for threat in candidates:
        try:
            previous_severity = threat.severity_level.upper()
            previous_classification = threat.classification
            result = analyze_log(threat.log_content)

            # Never let AI downgrade a higher-confidence deterministic finding.
            ai_severity = result["severity"]
            final_severity = previous_severity if _rank(previous_severity) >= _rank(ai_severity) else ai_severity

            ai_attack_type = result.get("attack_type", "UNKNOWN")
            if not threat.attack_type and ai_attack_type != "UNKNOWN":
                threat.attack_type = ai_attack_type

            if final_severity in {"HIGH", "CRITICAL"}:
                threat.classification = "ATTACK"
            elif result.get("classification") == "ATTACK":
                threat.classification = "ATTACK"
            elif result.get("classification") == "SUSPICIOUS" and threat.classification == "NORMAL":
                threat.classification = "SUSPICIOUS"

            threat.severity_level = final_severity
            threat.risk_score = max(threat.risk_score, _risk_from_severity(final_severity))
            threat.explanation = result.get("summary") or threat.explanation
            threat.ai_analyzed = True
            threat.ai_model = result.get("model", "")
            threat.ai_confidence = result.get("confidence", 0.0)
            threat.ai_summary = result.get("summary", "")
            threat.ai_recommendation = result.get("recommendation", "")
            threat.ai_indicators = result.get("indicators", [])
            threat.save(update_fields=[
                "classification", "severity_level", "risk_score", "attack_type",
                "explanation", "ai_analyzed", "ai_model", "ai_confidence",
                "ai_summary", "ai_recommendation", "ai_indicators"
            ])

            # Alert only when AI newly escalates a previously lower-risk event.
            escalated = (
                _rank(final_severity) > _rank(previous_severity)
                or (previous_classification != "ATTACK" and threat.classification == "ATTACK"
                    and _rank(final_severity) >= _rank("HIGH"))
            )
            if escalated and alert_service.should_alert(final_severity):
                alert_service.send_alert(threat)

        except Exception:
            logger.exception("AI analysis failed for ThreatLog %s", threat.pk)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        process_and_store_logs,
        trigger=IntervalTrigger(minutes=1),
        id="process_and_store_logs",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        process_ai_analysis,
        trigger=IntervalTrigger(minutes=1),
        id="process_ai_analysis",
        max_instances=1,
        replace_existing=True,
        next_run_time=timezone.now(),
    )

    register_events(scheduler)
    scheduler.start()
    print("Scheduler started. Monitoring logs with rule-based + Ollama AI analysis...")
