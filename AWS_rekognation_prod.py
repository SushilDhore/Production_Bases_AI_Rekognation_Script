import boto3
import environ

env = environ.Env()

def face_rekognition_function(image_name):
    BUCKET = env('AWS_RECOGNITION_BUCKET_NAME')
    # KEY = image_name
    KEY = f"static/{image_name}"
    region = 'us-east-1'
    def detect_labels(bucket, key, max_labels=10, min_confidence=90, region='us-east-1'):
        rekognition = boto3.client("rekognition", aws_access_key_id = env('AWS_RECOGNITION_ACCESS_KEY_ID'), aws_secret_access_key = env('AWS_RECOGNITION_ACCESS_KEY'), region_name = 'us-east-1')
        response = rekognition.detect_labels(
            Image={
            # "Bytes": image_string,
                "S3Object": {
                    "Bucket": env('AWS_RECOGNITION_BUCKET_NAME'),
                    "Name": KEY,
                }
            },
            MaxLabels=20,
            # MinConfidence=min_confidence,
        )
        return response
        # return response['Labels']
    function_result = detect_labels(BUCKET, KEY)
    restrict_list = ["People", "Family", "Number", "Weapon"]
    pass_list = ['Human', 'Person', 'Face']
    name_list = []
    results_list = []
    final_result_list = []
    for dict_obj in function_result["Labels"]:
        name_list.append(dict_obj["Name"])
    pass_count = 0
    for dict_obj in function_result["Labels"]:
        if dict_obj["Name"] in pass_list and dict_obj["Confidence"] > 96:
            # print(f'49-------name---{dict_obj["Name"]}-------Confidence-96--<-{dict_obj["Confidence"]}')
            pass_count += 1
    count = 0
    restriction = False
    for result in function_result["Labels"]:
        if result["Name"] in restrict_list and result["Confidence"] > 85:
            # print(f'54--------{result["Name"]}---------{restrict_list}')
            restriction = True
            count += 1
        elif (result["Name"] == "Kid" or result["Name"] == "Child") and result["Confidence"] > 60:
            # print(f'54--------{result["Name"]}---------{restrict_list}')
            restriction = True
            count += 1
        else:
            restriction = False
        final_result_list.append({"Name":result["Name"], "Confidence":result["Confidence"], "restriction_tag":restriction})
    # print(f'60-------count{count}---pass_count{pass_count}------final_result_list{final_result_list}')
    if count>0 or pass_count==0:
        return {"modified_result": final_result_list, "is_restricted": True}
    else:
        return {"modified_result": final_result_list, "is_restricted":
