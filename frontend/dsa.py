"""OrganFlow backend - every DSA structure is hand-written (no library stack/queue)."""
import heapq, itertools
from datetime import datetime, timedelta

# ---------------- DATA STRUCTURES ----------------
class _Node:
    __slots__ = ("data", "next")
    def __init__(self, data): self.data, self.next = data, None

class LinkedList:                     # organ journey
    def __init__(self): self.head = self.tail = None; self.size = 0
    def append(self, data):
        n = _Node(data)
        if self.tail: self.tail.next = n
        else: self.head = n
        self.tail = n; self.size += 1
    def to_list(self):
        out, c = [], self.head
        while c: out.append(c.data); c = c.next
        return out
    def __len__(self): return self.size

class Queue:                          # FIFO planned route (front -> rear)
    def __init__(self): self.front = self.rear = None; self.size = 0
    def enqueue(self, x):
        n = _Node(x)
        if self.rear: self.rear.next = n
        else: self.front = n
        self.rear = n; self.size += 1
    def dequeue(self):
        if not self.front: return None
        n = self.front; self.front = n.next
        if not self.front: self.rear = None
        self.size -= 1; return n.data
    def to_list(self):
        out, c = [], self.front
        while c: out.append(c.data); c = c.next
        return out
    def __len__(self): return self.size

class Stack:                          # audit trail (LIFO, top first)
    def __init__(self): self.top = None; self.size = 0
    def push(self, x):
        n = _Node(x); n.next = self.top; self.top = n; self.size += 1
    def pop(self):
        if not self.top: return None
        n = self.top; self.top = n.next; self.size -= 1; return n.data
    def to_list(self):
        out, c = [], self.top
        while c: out.append(c.data); c = c.next
        return out
    def __len__(self): return self.size

class PriorityQueue:                  # emergency transit (min-heap)
    def __init__(self): self._h = []; self._c = itertools.count()
    def push(self, priority, item): heapq.heappush(self._h, (priority, next(self._c), item))
    def pop(self): return heapq.heappop(self._h)[2] if self._h else None
    def __len__(self): return len(self._h)

def merge_sort(arr, key):             # stable O(n log n)
    if len(arr) <= 1: return arr[:]
    m = len(arr) // 2
    l, r = merge_sort(arr[:m], key), merge_sort(arr[m:], key)
    out, i, j = [], 0, 0
    while i < len(l) and j < len(r):
        if key(l[i]) <= key(r[j]): out.append(l[i]); i += 1
        else: out.append(r[j]); j += 1
    return out + l[i:] + r[j:]

# ---------------- DOMAIN RULES (simulation values) ----------------
MAX_HOURS = {"Heart": 4, "Lung": 6, "Kidney": 8, "Liver": 10, "Pancreas": 12}
BLOOD = ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"]
URG_RANK = {"High": 0, "Medium": 1, "Low": 2}
ABO_TO = {"O": "O A B AB", "A": "A AB", "B": "B AB", "AB": "AB"}
SAFE_TEMP = (2.0, 8.0)
ROUTE = ["Donor Hospital", "Ambulance Departed", "Transport Center",
         "Recipient Hospital", "Delivered"]

def blood_ok(donor, recip):
    d_abo, d_rh = donor[:-1], donor[-1]
    r_abo, r_rh = recip[:-1], recip[-1]
    return r_abo in ABO_TO[d_abo].split() and (d_rh == "-" or r_rh == "+")

def fmt_min(m):
    m = int(max(m, 0)); return f"{m // 60}h {m % 60:02d}m"

# ---------------- SYSTEM ----------------
class OrganFlow:
    def __init__(self, organs, recipients, hospitals):
        self.base = datetime.now().replace(second=0, microsecond=0)
        self.offset = 0
        self.organs, self.recipients, self.hospitals = organs, recipients, hospitals  # ArrayLists
        self.audit, self.journey, self.route = Stack(), {}, {}
        for o in self.organs:
            o["harvest_time"] = self.base - timedelta(minutes=int(o["harvest_offset_min"]))
            if o["status"] == "IN_TRANSIT":
                self._init_journey(o)
                self.route[o["organ_id"]].dequeue(); self.route[o["organ_id"]].dequeue()
                self.journey[o["organ_id"]].append(self._cp("Donor Hospital", o["harvest_time"] + timedelta(minutes=20), 4.5))
                self.journey[o["organ_id"]].append(self._cp("Ambulance Departed", o["harvest_time"] + timedelta(minutes=25), 4.8))
                r = self.find_recipient(o.get("recipient_id"))
                if r: r["status"] = "ALLOCATED"
        self.log("System", "Dataset loaded (synthetic)")

    # clock
    def now(self): return self.base + timedelta(minutes=self.offset)
    def advance_clock(self, mins): self.offset += mins; self.log("Clock", f"Simulation advanced +{mins} min")

    # audit (Stack)
    def log(self, action, detail=""):
        self.audit.push({"time": self.now().strftime("%d-%b %H:%M"), "action": action, "detail": detail})

    # linear searches
    def find_organ(self, oid):
        for o in self.organs:
            if o["organ_id"] == oid: return o
    def find_recipient(self, rid):
        for r in self.recipients:
            if r["recipient_id"] == rid: return r

    # registration
    def register_organ(self, organ_type, blood, hospital, elapsed_min=0):
        oid = f"O{101 + len(self.organs)}"
        self.organs.append({"organ_id": oid, "organ_type": organ_type, "blood_group": blood,
            "donor_hospital": hospital, "harvest_offset_min": elapsed_min, "status": "AVAILABLE",
            "recipient_id": "", "harvest_time": self.now() - timedelta(minutes=elapsed_min)})
        self.log("Organ registered", f"{oid} {organ_type} {blood} @ {hospital}"); return oid

    def add_recipient(self, name, organ, blood, urgency, days, hospital):
        rid = f"R{len(self.recipients) + 1:03d}"
        self.recipients.append({"recipient_id": rid, "name": name, "organ_needed": organ,
            "blood_group": blood, "urgency": urgency, "waiting_days": days,
            "hospital": hospital, "status": "WAITING"})
        self.log("Recipient added", f"{rid} needs {organ} {blood} ({urgency})"); return rid

    # module 1: matching = linear search + merge sort
    def match(self, oid):
        o = self.find_organ(oid); eligible, rejected = [], []
        for r in self.recipients:
            if r["status"] != "WAITING": continue
            if r["organ_needed"] != o["organ_type"]: reason = f"needs {r['organ_needed']}"
            elif not blood_ok(o["blood_group"], r["blood_group"]): reason = f"blood {r['blood_group']} incompatible"
            else: eligible.append(r); continue
            rejected.append({"recipient_id": r["recipient_id"], "reason": reason})
        ranked = merge_sort(eligible, key=lambda r: (URG_RANK[r["urgency"]], -int(r["waiting_days"])))
        return ranked, rejected

    # module 2: viability
    def viability(self, o):
        total = MAX_HOURS[o["organ_type"]] * 60
        elapsed = (self.now() - o["harvest_time"]).total_seconds() / 60
        rem = total - elapsed; pct = rem / total
        status = "EXPIRED" if rem <= 0 else "CRITICAL" if pct <= .25 else "WARNING" if pct <= .5 else "SAFE"
        return {"elapsed": elapsed, "remaining": rem, "pct": max(min(pct, 1), 0), "status": status}

    # module 4: journey (Queue route + LinkedList history)
    def _cp(self, loc, t, temp):
        ok = SAFE_TEMP[0] <= temp <= SAFE_TEMP[1]
        return {"location": loc, "time": t.strftime("%H:%M"), "temp_c": temp,
                "status": "SAFE" if ok else "COLD-CHAIN ALERT"}
    def _init_journey(self, o):
        q = Queue()
        for loc in ROUTE: q.enqueue(loc)
        self.route[o["organ_id"]] = q
        ll = LinkedList(); ll.append(self._cp("Harvested", o["harvest_time"], 4.0))
        self.journey[o["organ_id"]] = ll

    def start_transit(self, oid, rid):
        o, r = self.find_organ(oid), self.find_recipient(rid)
        self.log("Compatibility checked", f"{oid} vs candidates"); self.log("Recipient selected", f"{rid} for {oid}")
        o["status"], o["recipient_id"], r["status"] = "IN_TRANSIT", rid, "ALLOCATED"
        self._init_journey(o); self.log("Transit started", f"{oid} -> {r['hospital']}")

    # module 5: cold chain
    def advance(self, oid, temp):
        o = self.find_organ(oid); loc = self.route[oid].dequeue()
        if loc is None: return None
        cp = self._cp(loc, self.now(), temp); self.journey[oid].append(cp)
        self.log("Checkpoint updated", f"{oid} @ {loc} {temp}C")
        if cp["status"] != "SAFE": self.log("Cold-chain warning", f"{oid} {temp}C at {loc}")
        if loc == "Delivered":
            expired = self.viability(o)["status"] == "EXPIRED"
            o["status"] = "EXPIRED" if expired else "DELIVERED"
            self.find_recipient(o["recipient_id"])["status"] = "WAITING" if expired else "TRANSPLANT READY"
            self.log("Delivery completed", f"{oid} ({o['status']})")
        return cp

    # module 7: interruption
    def interrupt(self, oid, reason):
        o = self.find_organ(oid); o["status"] = "INTERRUPTED"
        v = self.viability(o); self.log("Transport interrupted", f"{oid}: {reason}")
        self.log("Emergency activated", f"{oid} remaining {fmt_min(v['remaining'])}")
    def resume(self, oid):
        self.find_organ(oid)["status"] = "IN_TRANSIT"; self.log("Transit resumed", oid)

    # module 3: emergency priority queue
    def emergency_board(self):
        pq = PriorityQueue()
        for o in self.organs:
            if o["status"] in ("IN_TRANSIT", "INTERRUPTED"):
                v = self.viability(o)
                urgent = o["status"] == "INTERRUPTED" or v["status"] in ("CRITICAL", "EXPIRED")
                pq.push((0 if urgent else 1, v["remaining"]), (o, v, urgent))
        rows = []
        while len(pq):
            o, v, urgent = pq.pop(); rows.append((o, v, urgent))
        return rows
