from datetime import datetime
import pandas as pd, os

os.makedirs("data", exist_ok=True)

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df = pd.DataFrame({"timestamp": [now]*5, "value": [1,2,3,4,5]})

out = f"data/sample_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(out, index=False)
print(f"[OK] wrote {out}")
