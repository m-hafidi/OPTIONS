"""Marks ``legacy/`` as a regular package so the engines are importable as
``legacy.option_pricing``.

That path is statically resolvable, which the Vercel function bundler needs in
order to include the package in the deployment. The Streamlit app and the local
API are unaffected: they import ``option_pricing`` directly (or via the package
path), and adding this file changes neither.
"""
