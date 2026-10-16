"""Shared response policy for static Pages assets and the streaming Worker."""
import json
from pathlib import Path

# The app renders with inline handlers, so scripts keep 'unsafe-inline'; eval is
# forbidden, and every other directive is locked to this origin plus the Firebase
# endpoints the sync module calls.
CONTENT_SECURITY_POLICY = '; '.join([
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https:",
    "font-src 'self' data:",
    "connect-src 'self' blob: data: https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://securetoken.googleapis.com",
    "worker-src 'self' blob:",
    "frame-src 'self' blob:",
    "media-src 'self' blob: data:",
    "manifest-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
])

HEADERS = {
    'Content-Security-Policy': CONTENT_SECURITY_POLICY,
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Cross-Origin-Opener-Policy': 'same-origin',
    'Cross-Origin-Resource-Policy': 'same-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=()',
}


def worker_source(source_url):
    return (Path(__file__).with_name('anatomy_pdf_worker.mjs').read_text()
            .replace('__ANATOMY_SOURCE_URL__', json.dumps(source_url))
            .replace('__WEB_SECURITY_HEADERS__', json.dumps(HEADERS)))
