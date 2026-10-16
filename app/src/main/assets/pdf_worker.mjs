/* PDF.js worker entry: the polyfills run before the worker module evaluates. */
import './pdf_polyfills.mjs';
import './vendor/pdfjs/pdf.worker.min.mjs';
