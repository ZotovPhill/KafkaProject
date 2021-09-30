#!/bin/sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --debug --reload --log-level=debug --timeout-keep-alive 0