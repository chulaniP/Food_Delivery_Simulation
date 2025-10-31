import random
import heapq
import statistics


# PARAMETERS 

SIM_TIME = 8 * 60 * 60        # 8 hours (seconds)
ARRIVAL_RATE = 1 / 90         # 1 order every 90 seconds
NUM_RIDERS = 10               # number of riders
RIDER_SPEED = 25.0            # km/h
AVG_DISTANCE = 4              # average distance to customer (km)
PREP_TIME_MEAN = 8 * 60       # avg prep time (8 mins)
PREP_TIME_STD = 2 * 60        # std dev (2 mins)
     # options: "nearest", "round_robin", "least_busy"

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def exp_interarrival(rate):
    return random.expovariate(rate)

def normal_prep_time(mean, std):
    t = random.gauss(mean, std)
    return max(60, t)  # at least 1 minute

def travel_time(distance_km, speed_kmh):
    return (distance_km / speed_kmh) * 3600  # in seconds

def draw_distance(avg_km):
    return random.expovariate(1 / avg_km)

# EVENT CLASS

class Event:
    def __init__(self, time, etype, data=None):
        self.time = time
        self.etype = etype
        self.data = data or {}
    def __lt__(self, other):
        return self.time < other.time


# SIMULATION FUNCTION

def run_simulation():
    random.seed(42)

    t = 0.0
    event_q = []
    order_id = 0
    ready_orders = []
    orders = {}
    riders = [{"state": "idle", "busy_time": 0.0} for _ in range(NUM_RIDERS)]
    next_rr = 0

    metrics = {"delivery_times": [], "dispatch_delays": [], "throughput": 0}

    # Schedule first order arrival
    heapq.heappush(event_q, Event(exp_interarrival(ARRIVAL_RATE), "order_arrival"))

    while event_q:
        ev = heapq.heappop(event_q)
        if ev.time > SIM_TIME:
            break
        t = ev.time

        if ev.etype == "order_arrival":
            # Generate new order
            order_id += 1
            prep = normal_prep_time(PREP_TIME_MEAN, PREP_TIME_STD)
            dist = draw_distance(AVG_DISTANCE)
            orders[order_id] = {"arrival": t, "prep_time": prep, "distance": dist}

            # Schedule prep done
            heapq.heappush(event_q, Event(t + prep, "prep_done", {"oid": order_id}))

            # Schedule next order
            heapq.heappush(event_q, Event(t + exp_interarrival(ARRIVAL_RATE), "order_arrival"))

        elif ev.etype == "prep_done":
            ready_orders.append(ev.data["oid"])
            # Try to assign to a rider
            assign_orders(t, ready_orders, riders, orders, event_q, next_rr)

        elif ev.etype == "pickup":
            rid = ev.data["rid"]
            oid = ev.data["oid"]
            dist = orders[oid]["distance"]
            delivery_time = travel_time(dist, RIDER_SPEED)
            orders[oid]["pickup_time"] = t
            heapq.heappush(event_q, Event(t + delivery_time, "delivered", {"rid": rid, "oid": oid}))
            
        #---- calculate dispatch delay--- 
            ready_time=orders[oid]["arrival"]+orders[oid]["prep_time"] 
            dispatch_delay=t-ready_time 
            if dispatch_delay >=0:
                
               metrics["dispatch_delays"].append(dispatch_delay) 
            heapq.heappush(event_q, Event(t + delivery_time, "delivered", {"rid": rid, "oid": oid}))    
        
        

        elif ev.etype == "delivered":
            rid = ev.data["rid"]
            oid = ev.data["oid"]
            riders[rid]["state"] = "idle"
            orders[oid]["delivery"] = t
            metrics["delivery_times"].append(t - orders[oid]["arrival"])
            metrics["throughput"] += 1
            # Rider becomes available again
            assign_orders(t, ready_orders, riders, orders, event_q, next_rr)

    # ---- Summary ----
    avg_delivery = statistics.mean(metrics["delivery_times"]) if metrics["delivery_times"] else 0
    avg_dispatch = statistics.mean(metrics["dispatch_delays"]) if metrics["dispatch_delays"] else 0
    print("\n=== SIMULATION RESULTS ===")
    print(f"Orders completed: {metrics['throughput']}")
    print(f"Average delivery time: {avg_delivery:.2f} seconds ({avg_delivery/60:.1f} min)")
    print(f"Average dispatch delay:{avg_dispatch:.2f} seconds({avg_dispatch/60:1f}min)")
    print(f"Total simulation time: {SIM_TIME/3600:.1f} hours")

# ----------------------------
# DISPATCH FUNCTION
# ----------------------------
def assign_orders(t, ready_orders, riders, orders, event_q, next_rr):
    if not ready_orders:
        return
    for rid, rider in enumerate(riders):
        if rider["state"] == "idle" and ready_orders:
            oid = ready_orders.pop(0)
            rider["state"] = "busy"
            dist_to_rest = random.uniform(0.2, 2.0)
            time_to_rest = travel_time(dist_to_rest, RIDER_SPEED)
            heapq.heappush(event_q, Event(t + time_to_rest, "pickup", {"rid": rid, "oid": oid}))

# ----------------------------
# RUN SIMULATION
# ----------------------------
if __name__ == "__main__":
    run_simulation()
