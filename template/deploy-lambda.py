from troposphere import (
    Template, iam, GetAtt, Join, Ref, logs, Select, Export, Output, Parameter, awslambda, Base64, ImportValue, Sub
)
from awacs.aws import Policy, Allow, Statement, Principal, Action

t = Template()

lambda_bucket = t.add_parameter(Parameter(
    "LambdaBucket",
    Type="String",
    Description="Bucket for lambda zip file"
))

lambda_package = t.add_parameter(Parameter(
    "LambdaPackage",
    Type="CommaDelimitedList",
    Description="Location of the zip"
))
# Create loggroup
log_group = t.add_resource(logs.LogGroup(
    "LogGroup",
    LogGroupName=Join("", ["/aws/lambda/", Join("-", ["lambda", Ref("AWS::StackName")])]),
    RetentionInDays=14
))

lambda_role = t.add_resource(iam.Role(
    "LambdaRole",
    AssumeRolePolicyDocument=Policy(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect=Allow,
                Principal=Principal("Service", "lambda.amazonaws.com"),
                Action=[Action("sts", "AssumeRole")]
            )
        ]),
    Path="/",
    ManagedPolicyArns=["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"],
    Policies=[
        iam.Policy(
            PolicyName="Deploy",
            PolicyDocument=Policy(
                Version="2012-10-17",
                Statement=[
                    Statement(
                        Effect=Allow,
                        Action=[
                            Action("iam", "PassRole"),
                        ],
                        Resource=["*"]
                    ),
                    Statement(
                        Effect=Allow,
                        Action=[
                            Action("cloudformation", "*"),
                        ],
                        Resource=["*"]
                    )
                ],
            )
        )
    ]
))

cfn_lambda = t.add_resource(awslambda.Function(
    "CfnLambda",
    DependsOn=["LogGroup"],  # log_group.title would also work
    Code=awslambda.Code(
        S3Bucket=Ref(lambda_bucket),
        S3Key=Ref(lambda_package)
    ),
    Handler="index.handler",
    FunctionName=Join("-", ["lambda", Ref("AWS::StackName")]),
    Role=GetAtt(lambda_role, "Arn"),
    Runtime="python3.3",
    Timeout=300,
    MemorySize=1536,
))

t.add_output(Output(
    "LambdaArn",
    Description="lambda arn",
    Value=GetAtt(cfn_lambda, "Arn"),
    Export=Export(
        Sub(
            "${AWS::StackName}-LambdaArn"
        )
    )
))

print(t.to_json())