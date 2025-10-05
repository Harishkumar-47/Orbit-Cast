# modules/risk.py

def classify(stats, var):
    value = stats["exceedance_chance"]
    
    if value > 75:
        return "🚨 Extreme Risk"
    elif value > 50:
        return "⚠️ High Risk"
    elif value > 25:
        return "🟡 Moderate Risk"
    else:
        return "🟢 Low Risk"
