#!/bin/bash
az storage blob list \
    --only-show-errors \
    --container-name $1 \
    --account-name $2 \
    --query "[*].[properties.contentLength]" \
    --output tsv | paste -s -d+ | bc
