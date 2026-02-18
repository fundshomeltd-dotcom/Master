from src.config.settings import settings


def menu_text() -> str:
    return "1. Today's Market Insight\n2. Top Gainers\n3. Risk Alert"


def optimize_ussd_text(text: str) -> str:
    cleaned = text.replace("\n", " ").strip()
    if settings.disclaimer not in cleaned:
        cleaned = f"{cleaned} {settings.disclaimer}".strip()
    return cleaned[:160]
