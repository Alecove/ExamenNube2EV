#!/bin/bash
# Script to create DynamoDB table quickly

aws dynamodb create-table \
    --table-name ContactMessages \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

echo "Table ContactMessages being created..."
