import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("lending_club")


def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        s3_file_name = event['Records'][0]['s3']['object']['key']

        resp = s3.get_object(Bucket=bucket_name, Key=s3_file_name)
        data = resp['Body'].read().decode("utf-8")
        loan = data.split("\n")
        for i in loan:
            print(i)
            loan_data = i.split(",")
            # Add data to dynamodb

            print("Before insert")
            table.put_item(
                Item={
                    "loan_ID": loan_data[0],
                    "loan_amnt": loan_data[1],
                    "term": loan_data[2],
                    "int_rate": loan_data[3],
                    "installment": loan_data[4],
                    "grade": loan_data[5],
                    "sub_grade": loan_data[6],
                    "emp_title": loan_data[7],
                    "emp_length": loan_data[8],
                    "home_ownership": loan_data[9],
                    "annual_inc": loan_data[10],
                    "verification_status": loan_data[11],
                    "issue_d": loan_data[12],
                    "loan_status": loan_data[13],
                    "purpose": loan_data[14],
                    "title": loan_data[15],
                    "dti": loan_data[16],
                    "earliest_cr_line": loan_data[19],
                    "open_acc": loan_data[20],
                    "pub_rec": loan_data[21],
                    "revol_bal": loan_data[22],
                    "revol_util": loan_data[23],
                    "total_acc": loan_data[24],
                    "initial_list_status": loan_data[25],
                    "application_type": loan_data[26],
                    "mort_acc ": loan_data[27],
                    "pub_rec_bankruptcies": loan_data[28],
                    "address": loan_data[29],
                })
            print("success")
    except Exception as e:
        print("EOF")













