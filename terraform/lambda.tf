resource "aws_iam_role" "punch_apollo_hr" {
  name = "punch_apollo_hr_role"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_iam_policy" "lambda_basic_execution" {
  name = "AWSLambdaBasicExecutionRole"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
          ]
          Effect   = "Allow"
          Resource = "*"
        }
      ]
      Version = "2012-10-17"
    }
  )
}

resource "aws_iam_role_policy_attachment" "punch_apollo_hr_role_policy_attachment" {
  role       = aws_iam_role.punch_apollo_hr.name
  policy_arn = aws_iam_policy.lambda_basic_execution.arn
}

data "archive_file" "lambda_punch_apollo_hr_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "punch_apollo_hr.zip"
}

resource "aws_lambda_function" "punch_apollo_hr" {
  function_name = "punch_apollo_hr"
  role          = aws_iam_role.punch_apollo_hr.arn
  architectures = ["arm64"]
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  memory_size   = "128"

  filename         = "punch_apollo_hr.zip"
  source_code_hash = data.archive_file.lambda_punch_apollo_hr_zip.output_base64sha256
  publish          = false
  environment {
    variables = {
      "COMPANY_CODE" = var.COMPANY_CODE
      "EMPLOYEE_NO"  = var.EMPLOYEE_NO
      "LOCATION"     = var.LOCATION
      "PASSWORD"     = var.PASSWORD
    }
  }
  timeout = 15
}

resource "aws_cloudwatch_event_rule" "weekdays_punch_in" {
  name                = "WeekdaysPunchIn"
  schedule_expression = "cron(42 1 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_rule" "weekdays_punch_out" {
  name                = "WeekdaysPunchOut"
  schedule_expression = "cron(52 10 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "punch_in_target" {
  rule = aws_cloudwatch_event_rule.weekdays_punch_in.name
  arn  = aws_lambda_function.punch_apollo_hr.arn
}

resource "aws_cloudwatch_event_target" "punch_out_target" {
  rule = aws_cloudwatch_event_rule.weekdays_punch_out.name
  arn  = aws_lambda_function.punch_apollo_hr.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_punch_in" {
  statement_id  = "allow_cloudwatch_punch_in"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.punch_apollo_hr.function_name
  source_arn    = aws_cloudwatch_event_rule.weekdays_punch_in.arn
  principal     = "events.amazonaws.com"
}

resource "aws_lambda_permission" "allow_cloudwatch_punch_out" {
  statement_id  = "allow_cloudwatch_punch_out"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.punch_apollo_hr.function_name
  source_arn    = aws_cloudwatch_event_rule.weekdays_punch_out.arn
  principal     = "events.amazonaws.com"
}

resource "aws_cloudwatch_log_group" "punch_apollo_hr" {
  name              = "/aws/lambda/punch_apollo_hr"
  retention_in_days = 3
  skip_destroy      = false
}
