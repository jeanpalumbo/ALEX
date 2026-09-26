#!/usr/bin/env python3
"""Start the CEO Console web server.

    python run_ceo_console.py

Then open http://<host>:<port>/ in a browser.
"""
import uvicorn

from aicommerce import config

if __name__ == "__main__":
    uvicorn.run("aicommerce.webapp.server:app", host=config.HOST, port=config.PORT, reload=False)
