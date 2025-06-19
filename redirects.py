import os
import json
import asyncio
from typing import Dict

class RedirectMap:
    """Thread-safe map of src_path → dst_path, persisted in redirects.json."""
    def __init__(self, filename="redirects.json"):
        # Usa um caminho absoluto para evitar ambiguidades
        self.path = os.path.join(os.getcwd(), filename)
        self._lock = asyncio.Lock()
        self.map: Dict[str, str] = {}
        # Carrega existentes, se houver
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.map = json.load(f)
            except Exception:
                self.map = {}

    async def add(self, src: str, dst: str):
        """Regista um redirect interno e persiste em disco."""
        # ignora self-redirects ou entradas já registadas
        if src == dst or self.map.get(src) == dst:
            return

        async with self._lock:
            self.map[src] = dst

            # função de escrita que fecha corretamente o ficheiro
            def _write():
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                with open(self.path, "w", encoding="utf-8") as f:
                    json.dump(self.map, f, ensure_ascii=False, indent=2)

            # executa a escrita em background, de forma síncrona
            await asyncio.to_thread(_write)

    def resolve(self, path: str) -> str:
        """Segue a cadeia de redirects até ao destino final."""
        while path in self.map:
            path = self.map[path]
        return path

# Instância global
redirects = RedirectMap()