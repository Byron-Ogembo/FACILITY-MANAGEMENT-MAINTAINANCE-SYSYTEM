import os
import json
import urllib.request
import urllib.error


# ─────────────────────────────────────────────
#  Knowledge-base builder  (RAG context)
# ─────────────────────────────────────────────
def _build_knowledge_context():
    """Query the live database and return a compact text snapshot."""
    try:
        from database.db import execute_query

        # Work orders summary
        wo_rows = execute_query(
            """SELECT wo.id, wo.title, wo.priority, wo.status,
                      e.name AS equipment, u.name AS technician
               FROM work_orders wo
               LEFT JOIN equipment e ON wo.equipment_id = e.id
               LEFT JOIN users u     ON wo.assigned_to   = u.id
               ORDER BY wo.id DESC LIMIT 20""",
            fetch_all=True
        ) or []

        # Equipment status
        eq_rows = execute_query(
            "SELECT name, category, location, status FROM equipment ORDER BY name",
            fetch_all=True
        ) or []

        # Inventory low-stock alert
        low_stock = execute_query(
            "SELECT part_name, quantity, reorder_level FROM inventory WHERE quantity <= reorder_level",
            fetch_all=True
        ) or []

        # Upcoming PM schedules
        pm_rows = execute_query(
            """SELECT ms.task_name, ms.frequency, ms.next_due_date,
                      e.name AS equipment, u.name AS assigned_to
               FROM maintenance_schedule ms
               LEFT JOIN equipment e ON ms.equipment_id = e.id
               LEFT JOIN users u     ON ms.assigned_to  = u.id
               WHERE ms.is_active = 1
               ORDER BY ms.next_due_date ASC LIMIT 10""",
            fetch_all=True
        ) or []

        # Staff list
        staff = execute_query(
            "SELECT name, role, email FROM users WHERE is_active = 1 ORDER BY role, name",
            fetch_all=True
        ) or []

        lines = ["=== TINDI CMMS LIVE KNOWLEDGE BASE ===\n"]

        lines.append("-- WORK ORDERS (latest 20) --")
        if wo_rows:
            for w in wo_rows:
                lines.append(
                    f"  WO#{w['id']}: {w['title']} | priority={w['priority']} "
                    f"status={w['status']} | equipment={w.get('equipment','N/A')} "
                    f"| assigned_to={w.get('technician','Unassigned')}"
                )
        else:
            lines.append("  No work orders found.")

        lines.append("\n-- EQUIPMENT STATUS --")
        if eq_rows:
            for eq in eq_rows:
                lines.append(
                    f"  {eq['name']} ({eq['category']}) @ {eq.get('location','?')} → {eq['status']}"
                )
        else:
            lines.append("  No equipment found.")

        lines.append("\n-- LOW-STOCK INVENTORY ITEMS --")
        if low_stock:
            for p in low_stock:
                lines.append(
                    f"  {p['part_name']}: qty={p['quantity']} (reorder level={p['reorder_level']})"
                )
        else:
            lines.append("  All inventory levels are sufficient.")

        lines.append("\n-- UPCOMING PREVENTIVE MAINTENANCE --")
        if pm_rows:
            for pm in pm_rows:
                lines.append(
                    f"  [{pm['next_due_date']}] {pm['task_name']} ({pm['frequency']}) "
                    f"on {pm.get('equipment','?')} → {pm.get('assigned_to','Unassigned')}"
                )
        else:
            lines.append("  No upcoming PM tasks.")

        lines.append("\n-- STAFF DIRECTORY --")
        if staff:
            for s in staff:
                lines.append(f"  {s['name']} | {s['role']} | {s['email']}")
        else:
            lines.append("  No staff found.")

        return "\n".join(lines)

    except Exception as exc:
        print(f"[chatbot] Knowledge-base build error: {exc}")
        return "Live CMMS data is temporarily unavailable."


# ─────────────────────────────────────────────
#  Main response function
# ─────────────────────────────────────────────
def get_chatbot_response(user_message, conversation_history):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Chatbot is temporarily unavailable (Missing API Key)."

    # Build live knowledge context (RAG)
    knowledge = _build_knowledge_context()

    system_prompt = {
        "role": "system",
        "content": (
            "You are Philron Assistant, the intelligent AI for TINDI CMMS — "
            "a Computerized Maintenance Management System for the Coca-Cola bottling plant. "
            "You have access to LIVE data from the system shown below. "
            "Use this data to answer questions about equipment status, work orders, "
            "inventory, staff assignments, and preventive maintenance schedules. "
            "Be concise, professional, and friendly. "
            "If asked about something not in the data, say so politely. "
            "Operating hours: Monday–Friday 8am–6pm.\n\n"
            + knowledge
        )
    }

    messages = [system_prompt] + list(conversation_history)
    messages.append({"role": "user", "content": user_message})

    payload = json.dumps({
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 512
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Groq API HTTP Error {e.code}: {body}")
        return "I'm having trouble connecting right now. Please try again in a moment."
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I'm having trouble connecting right now. Please try again in a moment."
