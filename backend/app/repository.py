from sqlalchemy import case, func, select

from app.models import Scan


def save_scan(db, scan_type, content, result):
    scan = Scan(
        scan_type=scan_type,
        input_preview=content.strip()[:200],
        prediction=result["prediction"],
        risk_score=result["risk_score"],
        risk_level=result.get("risk_level"),
        warning_signs=result.get("warning_signs", []),
    )
    db.add(scan)
    db.commit()


def scan_to_dict(scan):
    return {
        "id": scan.id,
        "scan_type": scan.scan_type,
        "input_preview": scan.input_preview,
        "prediction": scan.prediction,
        "risk_score": float(scan.risk_score),
        "risk_level": scan.risk_level,
        "warning_signs": scan.warning_signs,
        "created_at": scan.created_at.isoformat(),
    }


def get_dashboard(db, limit=10):
    phishing = case((Scan.prediction == "phishing", 1), else_=0)
    totals = db.execute(
        select(
            func.count(Scan.id),
            func.sum(phishing),
            func.avg(Scan.risk_score),
        )
    ).one()
    recent = db.scalars(
        select(Scan).order_by(Scan.created_at.desc()).limit(limit)
    ).all()
    total = totals[0] or 0
    phishing_count = totals[1] or 0

    return {
        "summary": {
            "total": total,
            "phishing": phishing_count,
            "legitimate": total - phishing_count,
            "average_risk": round(float(totals[2] or 0), 2),
        },
        "recent_scans": [scan_to_dict(scan) for scan in recent],
    }
