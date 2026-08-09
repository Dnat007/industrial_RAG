import os
import sys

from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

tenant_id = os.getenv("AZURE_TENANT_ID")
client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
deployment_name = os.getenv("FOUNDRY_CHAT_DEPLOYMENT")


# ============================================================
# 3. VALIDATE ENVIRONMENT VARIABLES
# ============================================================

required_variables = {
    "AZURE_TENANT_ID": tenant_id,
    "AZURE_CLIENT_ID": client_id,
    "AZURE_CLIENT_SECRET": client_secret,
    "FOUNDRY_PROJECT_ENDPOINT": project_endpoint,
    "FOUNDRY_CHAT_DEPLOYMENT": deployment_name,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    print("\nMissing environment variables:")

    for name in missing_variables:
        print(f"  - {name}")

    sys.exit(1)


print()
print("=" * 70)
print("MICROSOFT FOUNDRY DIRECT AUTHENTICATION TEST")
print("=" * 70)

print()
print("Configuration:")
print(f"Tenant ID       : {tenant_id}")
print(f"Client ID       : {client_id}")
print(f"Project endpoint: {project_endpoint}")
print(f"Deployment      : {deployment_name}")

# IMPORTANT:
# Never print AZURE_CLIENT_SECRET.


# ============================================================
# 4. CREATE CLIENT SECRET CREDENTIAL
# ============================================================

print()
print("[1/4] Creating Microsoft Entra credential...")

try:

    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    print("      SUCCESS")

except Exception as e:

    print("      FAILED")
    print()
    print(e)

    sys.exit(1)


# ============================================================
# 5. TEST MICROSOFT ENTRA TOKEN
# ============================================================

print()
print("[2/4] Requesting Microsoft Entra token...")

try:

    token = credential.get_token(
        "https://ai.azure.com/.default"
    )

    print("      SUCCESS")
    print(f"      Token length: {len(token.token)}")

except Exception as e:

    print("      FAILED")
    print()
    print("Microsoft Entra authentication failed:")
    print(e)

    credential.close()

    sys.exit(1)


# ============================================================
# 6. CREATE FOUNDRY PROJECT CLIENT
# ============================================================

print()
print("[3/4] Creating Microsoft Foundry Project client...")

try:

    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
    )

    print("      SUCCESS")

except Exception as e:

    print("      FAILED")
    print()
    print("Foundry Project connection failed:")
    print(e)

    credential.close()

    sys.exit(1)


# ============================================================
# 7. GET AUTHENTICATED OPENAI CLIENT
# ============================================================

print()
print("[4/4] Creating authenticated OpenAI client...")

try:

    openai_client = project_client.get_openai_client()

    print("      SUCCESS")

except Exception as e:

    print("      FAILED")
    print()
    print("OpenAI client creation failed:")
    print(e)

    project_client.close()
    credential.close()

    sys.exit(1)


# ============================================================
# 8. DIRECT MODEL INFERENCE
# ============================================================

print()
print("=" * 70)
print("TESTING DIRECT MODEL INFERENCE")
print("=" * 70)

print()
print(f"Deployment: {deployment_name}")

try:

    response = openai_client.responses.create(
        model=deployment_name,
        input="Reply with exactly: Azure authentication works.",
    )

    print()
    print("=" * 70)
    print("SUCCESS")
    print("=" * 70)

    print()
    print("Microsoft Entra authentication : SUCCESS")
    print("Foundry Project connection      : SUCCESS")
    print("OpenAI client                   : SUCCESS")
    print("Model inference                 : SUCCESS")

    print()
    print("Model response:")
    print(response.output_text)

    print()
    print("=" * 70)


except Exception as e:

    print()
    print("=" * 70)
    print("MODEL INFERENCE FAILED")
    print("=" * 70)

    print()
    print("Exact error:")
    print(e)

    print()
    print("=" * 70)


# ============================================================
# 9. CLEANUP
# ============================================================

try:
    openai_client.close()
except Exception:
    pass

try:
    project_client.close()
except Exception:
    pass

try:
    credential.close()
except Exception:
    pass
