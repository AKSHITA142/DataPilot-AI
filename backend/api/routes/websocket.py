from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.api.websocket_manager import ws_manager

router = APIRouter(prefix="/ws", tags=["Realtime WebSocket"])


@router.websocket("/jobs/{job_id}")
async def job_progress_websocket(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint streaming real-time research job status and progress events.
    Clients subscribe to job_id channels to receive live updates.
    """
    await ws_manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive & listen for client messages / pings
            data = await websocket.receive_text()
            # Send acknowledgement pong
            await websocket.send_json({"event": "pong", "job_id": job_id, "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)
    except Exception:
        ws_manager.disconnect(websocket, job_id)
