import argparse
import subprocess
import csv

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.subscription import SubscriptionClient

credential = DefaultAzureCredential()

def write_to_file(subscription_id: str, data):
    with open(f"{subscription_id}.csv","w") as file:
        writer = csv.writer(file)

        writer.writerow(["Account", "Service", "Value"])

        for account, services in data.items():
            for service, value in services.items():
                writer.writerow([account, service, value])

def human_readable_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)

    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} PB"  # fallback if > PB

def list_subscriptions()-> list[str]:
    subscription_ids = []
    subscription_client = SubscriptionClient(credential)

    for sub in subscription_client.subscriptions.list():
        subscription_ids.append(sub.subscription_id)

    return subscription_ids


def list_containers(storage_account_name: str)-> dict[str,int]:
    container_sizes = {}
    blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=credential)

    containers = blob_service_client.list_containers()
    for container in containers:
        print(f"[+] Container {container.name} ",end="")
        try:
            result = subprocess.run(
                ["./blob-size.sh", container.name , storage_account_name],
                capture_output=True,
                text=True
            )

            size_in_bytes = 0  if result.stdout == "" else int(result.stdout.strip())
            formatted_value = human_readable_size(size_in_bytes)
            container_sizes[container.name] = formatted_value

            print(f"Size: \033[94m{formatted_value}\033[0m")
        except:
            print(f"\t\033[91mError: Failed to get the size\033[0m")

    return  container_sizes
        
def list_storage_accounts(subscription_id: str)-> dict:
    storage_account_summary = {}
    storage_mgmt_client = StorageManagementClient(credential=DefaultAzureCredential(), subscription_id=subscription_id)
    storage_accounts  = storage_mgmt_client.storage_accounts.list()

    for account in storage_accounts:
        print(f"\033[92m[+]\033[0m Storage Account found: {account.name}")
        if(account.name):
            storage_account_summary[account.name] =  list_containers(account.name)
        else: 
            print("Error: Account name is null for some reason")

    return storage_account_summary

if __name__ == "__main__":
    subscription_ids = list_subscriptions()

    for subscription in subscription_ids:
        print(f"[*] Collecting data from : \033[95m{subscription}\033[0m")
        summary = list_storage_accounts(subscription)
        write_to_file(subscription,summary)


