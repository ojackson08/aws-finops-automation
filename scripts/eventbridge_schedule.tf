resource "aws_cloudwatch_event_rule" "weekly_finops" {
  name                = "weekly-finops-cleanup"
  description         = "Trigger FinOps Lambda every Sunday at 8am UTC"
  schedule_expression = "cron(0 8 ? * SUN *)"
}

resource "aws_cloudwatch_event_target" "finops_lambda" {
  rule      = aws_cloudwatch_event_rule.weekly_finops.name
  target_id = "FinOpsLambda"
  arn       = aws_lambda_function.finops.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.finops.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_finops.arn
}

resource "aws_lambda_function" "finops" {
  filename         = "lambda_package.zip"
  function_name    = "finops-ebs-cleanup"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "ebs_cleanup.lambda_handler"
  runtime          = "python3.10"
  source_code_hash = filebase64sha256("lambda_package.zip")
  timeout          = 60

  environment {
    variables = {
      SNS_TOPIC_ARN = var.sns_topic_arn
    }
  }
}
