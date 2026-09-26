import os
import json
from typing import Dict, Any
import aisuite as ai


MODEL_ID = "openai:gpt-4o-mini"
client = ai.Client()


# =====================================================================
# 1. SPECIALIZED AGENTS (Reservation & Claims)
# =====================================================================

class ReservationAgent:
    """Specialist agent for availabilities, flight, and hotel bookings."""
    
    def process(self, request_details: str, customer_email: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Reservation Specialist at a travel agency. "
                    "Process room/flight booking requests or availability searches. "
                    "Provide a structured outcome including status and booking references."
                ),
            },
            {
                "role": "user",
                "content": f"Customer ({customer_email}) request: {request_details}",
            },
        ]
        
        # Call model via aisuite
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages
        )
        return response.choices[0].message.content


class ClaimsAgent:
    """Specialist agent for complaints, flight delays, refunds, and policy checks."""
    
    def process(self, claim_details: str, customer_email: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Customer Claims Specialist at a travel agency. "
                    "Evaluate customer complaints, flight cancellation grievances, and refund claims. "
                    "Determine policy resolution and reimbursement decisions."
                ),
            },
            {
                "role": "user",
                "content": f"Customer ({customer_email}) claim: {claim_details}",
            },
        ]
        
        # Call model via aisuite
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages
        )
        return response.choices[0].message.content


# Instantiating downstream sub-agents
reservation_specialist = ReservationAgent()
claims_specialist = ClaimsAgent()


# =====================================================================
# 2. TOOLS & DELEGATION FUNCTIONS FOR FRONT DESK MAILING AGENT
# =====================================================================

def search_mail(query: str) -> str:
    """Searches the email inbox for unread or relevant customer emails.

    Args:
        query (str): Search term or filter, e.g., 'is:unread' or 'subject:booking'.
    """
    print(f"\n[TOOL EXECUTED] search_mail(query='{query}')")
    # Simulated incoming email inbox
    return json.dumps([
        {
            "mail_id": "MSG-901",
            "from": "sarah.connor@example.com",
            "subject": "Claim: Cancelled flight to Montreal",
            "snippet": "My flight was cancelled without notice..."
        }
    ])


def read_mail(mail_id: str) -> str:
    """Reads the full body and metadata of a specific customer email.

    Args:
        mail_id (str): Unique ID of the email to retrieve.
    """
    print(f"\n[TOOL EXECUTED] read_mail(mail_id='{mail_id}')")
    return json.dumps({
        "mail_id": mail_id,
        "from": "sarah.connor@example.com",
        "subject": "Claim: Cancelled flight to Montreal",
        "body": "Hello, my flight FL-402 to Montreal was cancelled yesterday without warning. I incurred $300 in unexpected hotel fees. I am requesting a full refund and hotel compensation."
    })


def send_mail(to: str, subject: str, body: str) -> str:
    """Sends a final email response to the customer.

    Args:
        to (str): Recipient email address.
        subject (str): Email subject line.
        body (str): Full text body of the response email.
    """
    print(f"\n=================== OUTGOING EMAIL ===================")
    print(f"To: {to}")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")
    print(f"======================================================")
    return "SUCCESS: Email delivered to customer."


def move_mail(mail_id: str, folder: str) -> str:
    """Moves an email to a target folder like 'Processed' or 'Archive'.

    Args:
        mail_id (str): Unique ID of the email.
        folder (str): Name of the destination folder.
    """
    print(f"\n[TOOL EXECUTED] move_mail(mail_id='{mail_id}', folder='{folder}')")
    return f"SUCCESS: Email {mail_id} moved to {folder}."


def delete_mail(mail_id: str) -> str:
    """Deletes an email from the inbox.

    Args:
        mail_id (str): Unique ID of the email to delete.
    """
    print(f"\n[TOOL EXECUTED] delete_mail(mail_id='{mail_id}')")
    return f"SUCCESS: Email {mail_id} deleted."


def delegate_to_reservation_agent(request_details: str, customer_email: str) -> str:
    """Delegates booking and availability requests to the Reservation Agent team.

    Args:
        request_details (str): Full context of the customer's booking request.
        customer_email (str): The email address of the customer making the request.
    """
    print(f"\n[DELEGATION] Routing task to Reservation Agent...")
    return reservation_specialist.process(request_details, customer_email)


def delegate_to_claims_agent(claim_details: str, customer_email: str) -> str:
    """Delegates complaints, refunds, and grievances to the Claims Agent (Customer Services) team.

    Args:
        claim_details (str): Full context of the customer's complaint or claim.
        customer_email (str): The email address of the customer submitting the claim.
    """
    print(f"\n[DELEGATION] Routing task to Claims Agent...")
    return claims_specialist.process(claim_details, customer_email)


# =====================================================================
# 3. AUTONOMOUS FRONT DESK RUNNER
# =====================================================================

def run_front_desk_agent():
    system_prompt = (
        "You are the Front Desk Autonomous Agent for a travel agency. "
        "Your job is to independently manage customer communications via email.\n\n"
        "Workflow Protocol:\n"
        "1. Search for unread emails (`search_mail`).\n"
        "2. Read the content of found emails (`read_mail`).\n"
        "3. Inspect customer intent and delegate to the right downstream specialist:\n"
        "   - Use `delegate_to_reservation_agent` for bookings, availabilities, or itinerary changes.\n"
        "   - Use `delegate_to_claims_agent` for complaints, refunds, or service grievances.\n"
        "4. Receive the specialist's resolution, compose a professional customer response, and send it (`send_mail`).\n"
        "5. Archive the handled email (`move_mail` to 'Processed')."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Check the inbox and process all incoming customer emails autonomously."}
    ]

    # Available tools passed as standard Python functions directly to aisuite
    tools_list = [
        search_mail,
        read_mail,
        send_mail,
        move_mail,
        delete_mail,
        delegate_to_reservation_agent,
        delegate_to_claims_agent,
    ]

    print("--- Autonomous Front Desk Agent Starting Loop ---")
    
    # max_turns allows aisuite to automatically handle multi-turn function calls
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        tools=tools_list,
        max_turns=10  # Allows up to 10 back-and-forth tool call execution cycles
    )

    print("\n--- Final Agent Execution Summary ---")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    run_front_desk_agent()