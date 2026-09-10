import json
import sys
from client import SerializableSnapshotIsolationEngine

ssi = SerializableSnapshotIsolationEngine()

def handle_rpc(line):
    try:
        req = json.loads(line)
        method = req.get("method")
        params = req.get("params", {})
        rid = req.get("id")
        
        if method == "tools/list":
            tools = [
                {"name": "record_antidependency", "description": "Track rw-antidependency between reader and writer"},
                {"name": "check_commit_safety", "description": "Check if transaction can commit without write-skew"}
            ]
            return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"tools": tools}})
        elif method == "tools/call":
            tname = params.get("name")
            args = params.get("arguments", {})
            if tname == "record_antidependency":
                ssi.register_antidependency(args["reader"], args["writer"])
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"status": "recorded"}})
            elif tname == "check_commit_safety":
                safe = ssi.can_commit(args["txn_id"])
                return json.dumps({"jsonrpc": "2.0", "id": rid, "result": {"safe": safe}})
    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    for line in sys.stdin:
        if line.strip():
            print(handle_rpc(line.strip()), flush=True)
