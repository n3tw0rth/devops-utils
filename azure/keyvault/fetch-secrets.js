const fs = require("fs");
const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");

async function main() {
  const credential = new DefaultAzureCredential();
  const url = `https://${process.env.KEYVAULT_NAME}.vault.azure.net`;
  const client = new SecretClient(url, credential);

  // NOTE: update the filter to fetch specific keys, keeping it empty return all the keys from the keyvault
  const filter = "";

  let secretsData = {};

  try {
    console.log("Fetching all secrets from Azure Key Vault...");

    // List all secret properties (names, but no values)
    for await (const secretProperties of client.listPropertiesOfSecrets()) {
      const secretName = secretProperties.name;
      if (secretName.includes(filter)) {
        // Fetch the actual secret value
        const secret = await client.getSecret(secretName);
        secretsData[secret.name] = secret.value;

        console.log(`Secret ${secretName} fetched successfully`);
      }
    }

    // Write secrets to a JSON file
    fs.writeFileSync("secrets.json", JSON.stringify(secretsData, null, 2));
    console.log("Secrets successfully saved to secrets.json");
  } catch (error) {
    console.error("An error occurred:", error);
    process.exit(1);
  }
}

main();
