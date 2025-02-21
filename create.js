const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");

const secrets = require("./secrets.json")

async function main() {
  const credential = new DefaultAzureCredential();

  const url = "https://" + process.env.KEYVAULT_NAME + ".vault.azure.net";

  const client = new SecretClient(url, credential);

  Object.keys(secrets).forEach(async secret => {
    const result = await client.setSecret(secret, secrets[secret]);
    console.log("result: ", result.name);
  })
}

main().catch((error) => {
  console.error("An error occurred:", error);
  process.exit(1);
});
