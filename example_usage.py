import sys
from client import SerializableSnapshotIsolationEngine

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def run():
    print(">>> Demonstrating Serializable Snapshot Isolation (SSI)...")
    ssi = SerializableSnapshotIsolationEngine()

    # Classical Write-Skew scenario:
    # T1 reads doctors on call (including doc 2), finds >= 2, sets doc 1 to off-call
    # T2 reads doctors on call (including doc 1), finds >= 2, sets doc 2 to off-call
    # Under regular SI, both commit leaving 0 doctors on call (anomaly).
    # Under SSI, rw-antidependency is tracked: T1 -> T2 and T2 -> T1.

    ssi.register_antidependency("T1", "T2") # T1 read doc 2 before T2 updated it
    ssi.register_antidependency("T2", "T1") # T2 read doc 1 before T1 updated it

    # Check pivots
    print(f"T1 is dangerous pivot: {ssi.is_dangerous_pivot('T1')}")
    print(f"T2 is dangerous pivot: {ssi.is_dangerous_pivot('T2')}")

    # SSI aborts the first transaction attempting commit if dangerous pivot detected
    assert ssi.can_commit("T1") is False
    print("SSI successfully prevented write-skew anomaly by aborting pivot transaction T1.")
    print("[PASS] Serializable Snapshot Isolation verified.")

if __name__ == "__main__":
    run()
