from fastapi import FastAPI
import requests

app = FastAPI()

def analyze_match(match_id):
    stats_url = f"https://api.sofascore.com/api/v1/event/{match_id}/statistics"
    graph_url = f"https://api.sofascore.com/api/v1/event/{match_id}/graph"

    stats = requests.get(stats_url).json()
    momentum = requests.get(graph_url).json()

    groups = stats["statistics"][0]["groups"]

    # Şutlar
    shots = groups[0]["statisticsItems"][0]
    shots_on_target = groups[0]["statisticsItems"][1]
    possession = groups[0]["statisticsItems"][2]
    corners = groups[0]["statisticsItems"][5]

    graph_data = momentum["graphData"][-15:]
    avg_momentum = sum([x["home"] for x in graph_data]) // len(graph_data)

    gol_ihtimali = min(100, (shots_on_target["home"] + shots_on_target["away"]) * 10 + avg_momentum // 2)
    korner_ihtimali = min(100, (corners["home"] + corners["away"]) * 7)

    return {
        "shots": {"home": shots["home"], "away": shots["away"]},
        "shots_on_target": {"home": shots_on_target["home"], "away": shots_on_target["away"]},
        "possession": {"home": possession["home"], "away": possession["away"]},
        "corners": {"home": corners["home"], "away": corners["away"]},
        "momentum_graph": [{"minute": i, "home": x["home"], "away": x["away"]} for i, x in enumerate(graph_data)],
        "gol_ihtimali": gol_ihtimali,
        "korner_ihtimali": korner_ihtimali
    }

@app.get("/live")
def live_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"
    data = requests.get(url).json()
    matches = []

    for event in data["events"]:
        match_id = event["id"]
        home = event["homeTeam"]["name"]
        away = event["awayTeam"]["name"]
        minute = event["time"]["currentPeriodStart"]

        analysis = analyze_match(match_id)

        matches.append({
            "home": home,
            "away": away,
            "minute": minute,
            "analysis": analysis
        })

    return {"matches": matches}
