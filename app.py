from constructs import Construct
from aws_cdk import (
    App, Stack,
    aws_lambda as _lambda,
    aws_apigateway as _apigw,
    Duration,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    CfnOutput,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3_deployment,
    RemovalPolicy,
    aws_lambda_python_alpha as lambda_python,
)
import json
import os

class ApiLambdaKBDemo(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Variaveis a serem alteradas

        bucket_nameFrontEnd = "wembleyapilambdakbdemo"
        KNOWLEDGE_BASE_ID = "CDOKDZYYWV"
        base_apiURL = "https://rt03q139eb.execute-api.us-east-1.amazonaws.com/prod/"

        # Cria uma camada da AWS Lambda a partir do arquivo local 'boto3.zip'
        boto3_layer = _lambda.LayerVersion(
            self, 'Boto3Layer',
            code=_lambda.AssetCode('./lambda_layer/boto3-mylayer.zip'),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
        )

        base_lambda = _lambda.Function(self, 'ApiLambdaKBDemo',
            handler='lambda_handler.lambda_handler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            environment={ # ADD THIS, FILL IT FOR ACTUAL VALUE 
                    "KNOWLEDGE_BASE_ID": KNOWLEDGE_BASE_ID
            },
            timeout=Duration.minutes(1),
            layers=[boto3_layer]
        )


        # Adiciona a política de permissão de bedrock
        bedrock_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:*"],
            resources=["*"],
        )

        # Adiciona a política de permissão à função Lambda
        base_lambda.add_to_role_policy(bedrock_policy)

        base_api = _apigw.RestApi(self, 'ApiGatewayKBDemo',
                                  rest_api_name='ApiGatewayKBDemo')
        MAP_PARAMETER = {
            "filter": "$input.params('filter')",
            "prompt": "$input.params('prompt')"
        }
        example_entity = base_api.root.add_resource(
            'kb',
            default_cors_preflight_options=_apigw.CorsOptions(
                allow_methods=['GET', 'OPTIONS'],
                allow_origins=_apigw.Cors.ALL_ORIGINS)
        )
        example_entity_lambda_integration = _apigw.LambdaIntegration(
            base_lambda,
            proxy=False,
            request_templates={
                "application/json": json.dumps(MAP_PARAMETER)
            },
            integration_responses=[
                _apigw.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        
        example_entity.add_method(
            'GET', example_entity_lambda_integration,
            request_parameters={'method.request.querystring.prompt':False,
                'method.request.querystring.filter':False
            },
                
            method_responses=[
                _apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )

        # Cria o bucket S3 para armazenar os arquivos de origem
        origin_bucket = s3.Bucket(
            self,
            "OriginBucket",
            bucket_name=bucket_nameFrontEnd
        )
        # Cria a origem da distribuição CloudFront
        origin = origins.S3Origin(origin_bucket)

        # Cria a distribuição CloudFront
        distribution = cloudfront.Distribution(
            self,
            "CloudFrontDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(origin=origin),
        )

        # Exporta o nome do domínio da distribuição CloudFront
        CfnOutput(
            self,
            "DistributionDomainName",
            value=distribution.distribution_domain_name,
            description="CloudFront Distribution Domain Name",
        )

        # Ler o conteúdo do arquivo index.html
        with open("./frontend_template/index_template.html", "r") as file:
            html_content = file.read()

        # Substituir as variáveis no conteúdo do HTML
        html_content = html_content.replace("BASE_URL", base_apiURL)

        # Criar o diretório "frontend" se ele não existir
        if not os.path.exists("./frontend"):
            os.makedirs("./frontend")

        # Gravar o conteúdo renderizado em um novo arquivo index.html
        with open("./frontend/index.html", "w") as file:
            file.write(html_content)

        s3_deployment.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[s3_deployment.Source.asset("./frontend")],
            destination_bucket=origin_bucket
        )

app = App()
ApiLambdaKBDemo(app, "ApiLambdaKBDemo")
app.synth()