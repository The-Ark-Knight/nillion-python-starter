from pdb import set_trace as bp
import argparse
import asyncio
import py_nillion_client as nillion
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from helpers.nillion_client_helper import create_nillion_client

load_dotenv()

# Store and retrieve a SecretInteger using the Python Client
async def main():
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    userkey_path = os.getenv("NILLION_WRITERKEY_PATH")
    userkey = nillion.UserKey.from_file(userkey_path)
    client = create_nillion_client(userkey)

    # Create a SecretInteger
    secret_name = "my_int1"
    secret_value = 100
    secret_integer = nillion.Secrets({
        secret_name: nillion.SecretInteger(secret_value),
    })

    # Store a SecretInteger 
    # Notice that both bindings and permissions are set to None
    # Bindings need to be set to use secrets in programs
    # Permissions need to be set to allow users other than the secret creator to use the secret
    store_id = await client.store_secrets(
        cluster_id, None, secret_integer, None
    )

    print(f"The secret is stored at store_id: {store_id}")

    result = await client.retrieve_secret(cluster_id, store_id, secret_name)
    print(f"The secret value is {result[1].value}")

asyncio.run(main())