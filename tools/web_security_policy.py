"""Shared response policy for static Pages assets and the streaming Worker."""
import json
from pathlib import Path

HEADERS = {
    'Content-Security-Policy': "frame-ancestors 'none'",
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
}


def worker_source(source_url):
    return (Path(__file__).with_name('anatomy_pdf_worker.mjs').read_text()
            .replace('__ANATOMY_SOURCE_URL__', json.dumps(source_url))
            .replace('__WEB_SECURITY_HEADERS__', json.dumps(HEADERS)))
