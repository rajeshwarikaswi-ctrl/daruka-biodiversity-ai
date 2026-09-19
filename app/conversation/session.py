import uuid
from collections import defaultdict
from typing import Dict, List, Any
from app.schemas import LandContext

class SessionStore:
    def __init__(self):
        self._turns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._ctx: Dict[str, LandContext] = {}

    def new_id(self) -> str:
        return str(uuid.uuid4())

    def get_ctx(self, sid: str) -> LandContext:
        return self._ctx.get(sid, LandContext())

    def update_ctx(self, sid: str, new_ctx: LandContext) -> LandContext:
        merged = self.get_ctx(sid).model_copy()
        for k, v in new_ctx.model_dump(exclude_none=True).items():
            setattr(merged, k, v)
        self._ctx[sid] = merged
        return merged

    def add_turn(self, sid: str, role: str, content: str):
        self._turns[sid].append({"role": role, "content": content})

    def history(self, sid: str) -> List[Dict[str, Any]]:
        return self._turns.get(sid, [])

store = SessionStore()
