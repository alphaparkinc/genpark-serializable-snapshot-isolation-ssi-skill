class SerializableSnapshotIsolationEngine:
    """
    Serializable Snapshot Isolation (SSI) engine.
    Tracks rw-antidependencies (si-edges) between concurrent transactions
    and aborts the pivot transaction in any dangerous consecutive edge pair (T1 -> T2 -> T3).
    """
    def __init__(self):
        self.committed_txns = {}
        self.in_in_edges = {} # txn -> set of incoming antidependency sources
        self.out_edges = {} # txn -> set of outgoing antidependency targets
        self.clock = 0

    def register_antidependency(self, reader_txn, writer_txn):
        """reader_txn has an rw-antidependency to writer_txn (reader read old version before writer created new one)."""
        if reader_txn not in self.out_edges:
            self.out_edges[reader_txn] = set()
        self.out_edges[reader_txn].add(writer_txn)

        if writer_txn not in self.in_in_edges:
            self.in_in_edges[writer_txn] = set()
        self.in_in_edges[writer_txn].add(reader_txn)

    def is_dangerous_pivot(self, txn_id):
        """A transaction is a dangerous pivot if it has both an incoming and outgoing rw-antidependency."""
        has_in = len(self.in_in_edges.get(txn_id, [])) > 0
        has_out = len(self.out_edges.get(txn_id, [])) > 0
        return has_in and has_out

    def can_commit(self, txn_id):
        # SSI rule: abort if txn is a pivot in a cycle of antidependencies
        if self.is_dangerous_pivot(txn_id):
            return False
        return True
