"""
EnviroHealth AI — Sensor Simulator
Generates realistic sensor data and sends it to the backend.

Usage:
  python simulator.py --mode normal
  python simulator.py --mode high_pollution
  python simulator.py --mode water_contamination
  python simulator.py --mode heatwave
  python simulator.py --once   # Send one batch and exit
"""
import asyncio
import aiohttp
import argparse
import random
import json
from datetime import datetime, timezone


BASE_URL = "http://localhost:8000/api/v1/sensors/readings"

SENSORS = [
    {"code": "AIR-G101-001", "type": "air"},
    {"code": "AIR-G102-001", "type": "air"},
    {"code": "WTR-G101-001", "type": "water"},
    {"code": "WTR-G102-001", "type": "water"},
    {"code": "WTH-G103-001", "type": "weather"},
    {"code": "AIR-G108-001", "type": "air"},
]


def generate_readings(sensor_code: str, sensor_type: str, mode: str) -> dict:
    ts = datetime.now(timezone.utc).isoformat()

    if sensor_type == "air":
        base = {"normal": 80, "high_pollution": 220, "heatwave": 140, "water_contamination": 80}[mode]
        readings = {
            "pm25": round(base * 0.5 * random.uniform(0.9, 1.1), 1),
            "pm10": round(base * 0.75 * random.uniform(0.9, 1.1), 1),
            "aqi": round(base * random.uniform(0.95, 1.05), 1),
            "temperature": round({"normal": 30, "high_pollution": 33, "heatwave": 43, "water_contamination": 31}[mode] + random.uniform(-1, 1), 1),
            "humidity": round({"normal": 60, "high_pollution": 65, "heatwave": 25, "water_contamination": 70}[mode] + random.uniform(-5, 5), 1),
        }
    elif sensor_type == "water":
        readings = {
            "water_ph": round({"normal": 7.2, "high_pollution": 7.0, "heatwave": 7.4, "water_contamination": 5.8}[mode] + random.uniform(-0.1, 0.1), 2),
            "water_tds": round({"normal": 280, "high_pollution": 350, "heatwave": 320, "water_contamination": 750}[mode] + random.uniform(-20, 20), 1),
            "water_turbidity": round({"normal": 0.8, "high_pollution": 1.5, "heatwave": 1.2, "water_contamination": 18.5}[mode] + abs(random.gauss(0, 0.2)), 2),
            "water_temperature": round({"normal": 22, "high_pollution": 24, "heatwave": 29, "water_contamination": 23}[mode] + random.uniform(-1, 1), 1),
        }
    else:  # weather
        readings = {
            "temperature": round({"normal": 30, "high_pollution": 33, "heatwave": 45, "water_contamination": 30}[mode] + random.uniform(-2, 2), 1),
            "humidity": round({"normal": 60, "high_pollution": 65, "heatwave": 20, "water_contamination": 75}[mode] + random.uniform(-5, 5), 1),
            "rainfall": round(max(0, {"normal": 2, "high_pollution": 0, "heatwave": 0, "water_contamination": 15}[mode] + random.gauss(0, 2)), 1),
            "wind_speed": round(random.uniform(5, 25), 1),
        }

    return {"sensor_code": sensor_code, "timestamp": ts, "readings": readings}


async def send_reading(session: aiohttp.ClientSession, payload: dict, verbose: bool = True):
    try:
        async with session.post(BASE_URL, json=payload) as resp:
            if verbose:
                status = "✅" if resp.status == 201 else "⚠️"
                print(f"  {status} {payload['sensor_code']} → {resp.status}")
            return resp.status
    except Exception as e:
        print(f"  ❌ {payload['sensor_code']} → Error: {e}")
        return None


async def run_simulator(mode: str = "normal", interval: int = 30, once: bool = False):
    print(f"🛰  EnviroHealth AI Sensor Simulator")
    print(f"   Mode: {mode.upper()}")
    print(f"   Target: {BASE_URL}")
    print(f"   Sensors: {len(SENSORS)}")
    print()

    async with aiohttp.ClientSession() as session:
        while True:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sending readings...")
            for s in SENSORS:
                payload = generate_readings(s["code"], s["type"], mode)
                await send_reading(session, payload)
            print()

            if once:
                break
            await asyncio.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="EnviroHealth AI Sensor Simulator")
    parser.add_argument("--mode", choices=["normal", "high_pollution", "water_contamination", "heatwave"],
                        default="normal")
    parser.add_argument("--interval", type=int, default=30, help="Seconds between batches")
    parser.add_argument("--once", action="store_true", help="Send one batch and exit")
    args = parser.parse_args()
    asyncio.run(run_simulator(args.mode, args.interval, args.once))


if __name__ == "__main__":
    main()
