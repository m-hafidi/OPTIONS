"""Marks ``server/`` as a package for the Vercel entrypoint ``server.main:app``.

Locally the API still runs as a top-level module: ``npm run api`` → uvicorn
``main:app`` with this directory on ``sys.path``.
"""
