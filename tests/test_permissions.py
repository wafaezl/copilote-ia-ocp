import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_server.permissions import est_autorise, lister_permissions

# Cas autorises
print("agent_ingestion peut appeler load_dataset ?", est_autorise("agent_ingestion", "load_dataset"))
print("agent_kpi peut appeler compute_kpis ?", est_autorise("agent_kpi", "compute_kpis"))

# Cas NON autorises (important a verifier aussi)
print("agent_ingestion peut appeler compute_kpis ?", est_autorise("agent_ingestion", "compute_kpis"))
print("agent_preparation peut appeler load_dataset ?", est_autorise("agent_preparation", "load_dataset"))

print("\nOutils autorises pour agent_kpi :", lister_permissions("agent_kpi"))