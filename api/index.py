"""All same-origin UI/API requests use the existing role-checked handler."""
from math_quest_server import Handler
from math_quest_cloud import CloudApp
from urllib.parse import urlparse,parse_qs,urlencode

class handler(Handler):
    def do_GET(self):self._serve(super().do_GET)
    def do_POST(self):self._serve(super().do_POST)
    def _serve(self,operation):
        try:
            self.server=CloudApp()
            parsed=urlparse(self.path);query=parse_qs(parsed.query);route=query.pop('mq_path',[None])[0]
            if route is not None:
                if not route.startswith('/') or route.startswith('//'):return self.reply(400,{'error':'주소를 확인해 주세요.'})
                self.path=route+('?' + urlencode(query,doseq=True) if query else '')
            return operation()
        except Exception:
            # Do not expose connection strings, storage credentials, or SQL diagnostics.
            return self.reply(503,{'error':'서버 연결을 확인하고 잠시 뒤 다시 시도해 주세요.'})
