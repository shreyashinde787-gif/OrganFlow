# Planned Java API adapter (not implemented in this demo)

The current Streamlit demo is self-contained and runs the DSA engine in `frontend/dsa.py`.
The Java source in `java-lab/SmartOrganTracker.java` is preserved for the college lab. This contract records a future integration plan; it is not a live API.

Suggested endpoints for a future Java REST adapter:
- `GET /api/dashboard`
- `GET /api/organs`
- `POST /api/organs`
- `GET /api/recipients`
- `POST /api/recipients`
- `GET /api/matching/{organId}`
- `POST /api/transit/{organId}/start`
- `POST /api/transit/{organId}/checkpoint`
- `POST /api/transit/{organId}/interrupt`
- `POST /api/transit/{organId}/resume`
- `GET /api/viability`
- `GET /api/audit`

Do not point the Streamlit app at localhost:8080 until the Java API is actually implemented and running.
