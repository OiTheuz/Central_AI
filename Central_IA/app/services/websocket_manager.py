from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Mapeia schema -> lista de WebSockets ativos para aquele lojista
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, schema: str):
        await websocket.accept()
        if schema not in self.active_connections:
            self.active_connections[schema] = []
        self.active_connections[schema].append(websocket)
        logger.info(f"WebSocket conectado no schema: {schema}. Total: {len(self.active_connections[schema])}")

    def disconnect(self, websocket: WebSocket, schema: str):
        if schema in self.active_connections:
            if websocket in self.active_connections[schema]:
                self.active_connections[schema].remove(websocket)
                logger.info(f"WebSocket desconectado no schema: {schema}.")
            if len(self.active_connections[schema]) == 0:
                del self.active_connections[schema]

    async def broadcast_to_schema(self, schema: str, message: dict):
        if schema in self.active_connections:
            # Create a copy of the list to avoid RuntimeError if a client disconnects during broadcast
            connections = list(self.active_connections[schema])
            for connection in connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Falha ao enviar mensagem WebSocket no schema {schema}: {e}")

manager = ConnectionManager()
