import io
import sys
from typing import Any, Dict, List
import aisuite as ai

# ==========================================
# 1. Email Tools (Native Functions)
# ==========================================

def search_mail(query: str) -> List[str]:
    """Recherche des e-mails par mot-clé."""
    print(f"  [Tool Executed] search_mail(query='{query}')")
    return [f"mail_101 (Sujet: {query})", f"mail_102 (Sujet: Re: {query})"]

def read_mail(mail_id: str) -> str:
    """Lit le contenu d'un e-mail à partir de son ID."""
    print(f"  [Tool Executed] read_mail(mail_id='{mail_id}')")
    return f"Contenu de {mail_id} : 'Veuillez valider le budget Q3 avant 17h.'"

def write_reply(mail_id: str, body: str) -> str:
    """Répond à un e-mail spécifié."""
    print(f"  [Tool Executed] write_reply(mail_id='{mail_id}', body='{body}')")
    return f"Réponse envoyée à {mail_id}."

def move_mail(mail_id: str, folder: str) -> str:
    """Déplace un e-mail vers un dossier."""
    print(f"  [Tool Executed] move_mail(mail_id='{mail_id}', folder='{folder}')")
    return f"E-mail {mail_id} déplacé vers '{folder}'."

def delete_mail(mail_id: str) -> str:
    """Supprime un e-mail."""
    print(f"  [Tool Executed] delete_mail(mail_id='{mail_id}')")
    return f"E-mail {mail_id} supprimé."

# ==========================================
# 2. Agent Code Execution with AISuite
# ==========================================

SYSTEM_PROMPT = """
Tu es un agent d'automatisation d'e-mails.
Génère et exécute du code Python pour répondre à la demande de l'utilisateur.

Les fonctions suivantes sont DÉJÀ importées et disponibles directement dans ton code :
- search_mail(query: str) -> list
- read_mail(mail_id: str) -> str
- write_reply(mail_id: str, body: str) -> str
- move_mail(mail_id: str, folder: str) -> str
- delete_mail(mail_id: str) -> str

Règles :
1. Génère uniquement un bloc de code Python exécutable sans explications additionnelles.
2. Utilise les fonctions listées ci-dessus.
3. Utilise print() pour afficher le résultat final.
"""

class AISuiteCodeGeneratingAgent:
    def __init__(self, model_provider: str = "openai:gpt-4o-mini"):
        # Initialize AISuite client
        self.client = ai.Client()
        self.model_provider = model_provider
        
        # Execution environment pre-loaded with local email tools
        self.execution_environment = {
            "search_mail": search_mail,
            "read_mail": read_mail,
            "write_reply": write_reply,
            "move_mail": move_mail,
            "delete_mail": delete_mail,
        }

    def run(self, user_prompt: str):
        print(f"Demande Utilisateur : \"{user_prompt}\"\n")

        # 1. Code generation via AISuite interface
        response = self.client.chat.completions.create(
            model=self.model_provider,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )

        generated_code = response.choices[0].message.content

        # Strip Markdown code blocks
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0].strip()

        print("--- Code Python Généré via AISuite ---")
        print(generated_code)
        print("--------------------------------------\n")

        # 2. Dynamic execution within the tool environment
        print("--- Exécution du Code ---")
        buffer = io.StringIO()
        sys.stdout = buffer

        try:
            exec(generated_code, self.execution_environment)
            sys.stdout = sys.__stdout__
            print("Résultat de l'exécution (stdout) :")
            print(buffer.getvalue().strip())
        except Exception as e:
            sys.stdout = sys.__stdout__
            print(f"Erreur d'exécution : {e}")

# ==========================================
# 3. Execution
# ==========================================

if __name__ == "__main__":
    # Uses gpt-4o-mini via AISuite
    agent = AISuiteCodeGeneratingAgent(model_provider="openai:gpt-4o-mini")

    prompt = (
        "Cherche les e-mails sur le 'budget', lis le premier e-mail trouvé (mail_101), "
        "réponds 'C'est validé !', puis déplace cet e-mail dans le dossier 'Archive'."
    )

    agent.run(prompt)