# Catching Femi-simp Flat 85 SeATon 
## Introduction
This game is about catching Seaton. You can think of Seaton as a somewhat foolish yet notorious criminal who often operates within the community, particularly around Flat85. While he is skilled at hiding himself, he unintentionally emits signals to the outside world. By detecting these signals, we can track his location and help the police apprehend him.

## Seaton Tracker: Signal-Based Localization System**  
=================================================

This project simulates the tracking of **Seaton** — a foolish criminal who unintentionally emits TCP-based signals while moving around **Flat85**. The system consists of two main components:  
1. A **TCP latency measurement server** that collects signal data  
2. A **Monte Carlo simulator** that estimates Seaton's location based on signal latency patterns

## Mathematical Principle

The localization of Mr. Seaton is achieved using a Time Difference of Arrival (TDoA) method with signals received at four known server locations.

Signal Reception: Four servers (Hong Kong, Seoul, Russia, UK) receive a signal from Mr. Seaton at times $t_1, t_2, t_3, t_4$.

Proportional Relationship: The time of arrival at each server is proportional to the distance from Seaton's location. Thus:
$dᵢ = c * tᵢ$
where $dᵢ$ is the distance to server $i$, and $c$ is the constant signal propagation speed (to be determined).

Trilateration (3 Circles): Using the first three servers $(t_1, t_2, t_3)$, we can form three circles centered at each server's location with radii $c*t_1, c*t_2, c*t_3$. In theory, these three circles intersect at a single point, which is Seaton's unique location $(x, y)$.

Solving for the Constant c: The fourth server provides the necessary constraint to solve for the unknown constant c. The measured time t₄ must satisfy the distance equation for the fourth server:
$$
distance( (x, y), Server₄ ) = c * t₄
$$
By substituting the location $(x, y)$ found from the first three points, we can solve this equation for the exact value of $c$.

Final Localization: With $c$ known, the precise distances to all servers are calculated, yielding Mr. Seaton's exact coordinates through geometric intersection.

This method combines trilateration with a time-to-distance scaling factor solved via an over-determined system, ensuring accurate and unique localization.

## 🛠️ Prerequisites  
- Python 3.7+
- Required packages: `numpy`, `matplotlib` (for visualization)

Install dependencies:
```bash
pip install numpy matplotlib
```

---

## 🧠 How It Works

1. **Seaton's device** periodically emits TCP signals (simulated via latency measurements)
2. The TCP server collects latency values which correlate with distance
3. The Monte Carlo simulation uses these latency measurements to probabilistically estimate his position around Flat85

---

## 🚀 Usage Instructions

### Step 1: Start the TCP Server
Open a terminal and run:
```bash
python tcp_latency_measurement.py server
```

You should see:
```
TCP Server started on port 12345...
Waiting for client connections...
```

### Step 2: Simulate Seaton's Signal Transmission
Open another terminal and run the client to simulate Seaton emitting signals:
```bash
python tcp_latency_measurement.py client --count 20 --interval 0.5
```

This will:
- Send 20 TCP packets to the server
- Wait 0.5 seconds between each packet
- Measure latency for each transmission

### Step 3: Run the Monte Carlo Localization
Open a third terminal and run:
```bash
python monte_carlo_simulation.py
```

This script will:
- Connect to the TCP server to retrieve latency measurements
- Convert latency values to distance estimates
- Run Monte Carlo simulation with 10,000 particles
- Output Seaton's most probable location

---

## 📊 Example Output

**TCP Server Output:**
```
Received packet 1 - Latency: 42.3 ms
Received packet 2 - Latency: 38.1 ms
...
20 packets received. Average latency: 40.2 ms
```

**Monte Carlo Simulation Output:**
```
Running Monte Carlo simulation with 10000 particles...
Most probable Seaton location: (42.15, -71.08)
Estimated accuracy: ±5.2 meters
```

---

## 📁 File Structure

```
├── tcp_latency_measurement.py  # TCP server/client for signal measurement
├── monte_carlo_simulation.py   # Location estimation using particle filter
├── config.py                   # Configuration parameters
└── README.md
```

---

## ⚙️ Configuration Options

Modify `config.py` to adjust:
- **TCP_PORT**: Server listening port (default: 12345)
- **LATENCY_TO_DISTANCE_RATIO**: Conversion factor from ms to meters
- **SIMULATION_BOUNDS**: Area boundaries around Flat85
- **PARTICLE_COUNT**: Number of particles in simulation (default: 10000)

---

## 🎯 Customization

- Adjust `--count` and `--interval` in client command to change signal frequency
- Modify noise model in `monte_carlo_simulation.py` for different environments
- Change visualization settings in the simulation script

---

## 📝 Notes

- Ensure the TCP server is running before starting the client
- The simulation assumes a 2D coordinate system around Flat85
- Latency values are converted to distance using configurable ratio
- Higher particle count improves accuracy but increases computation time

---

**Happy Seaton hunting!** 🕵️♂️
