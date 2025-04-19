#!/bin/bash

aws_profile=$1
lambda_function_name=$2
lambda_function_dir=$3
lambda_function_zip="$lambda_function_name.zip"

# copy shared directory to the lambda function directory
cp -r shared $lambda_function_dir

# Create a zip file with the specified files
cd $lambda_function_dir && zip -r ../$lambda_function_zip . && cd ..

# Check if the zip operation was successful
if [ $? -eq 0 ]; then
    echo "Zip file created successfully."
else
    echo "Failed to create zip file."
    exit 1
fi

# Upload the zip file to AWS Lambda
aws lambda update-function-code --profile $aws_profile --function-name $lambda_function_name --zip-file fileb://$lambda_function_zip > /dev/null 2>&1

# Check if the AWS Lambda update was successful
if [ $? -eq 0 ]; then
    echo "Lambda function updated successfully."
else
    echo "Failed to update Lambda function."
    exit 1
fi

rm $lambda_function_zip
rm -r $lambda_function_dir/shared


# run example: bash deploy-lambda.sh <aws_profile> <lambda_function_name> <lambda_function_dir>
# bash deploy-lambda.sh otterlab pencilo-text text