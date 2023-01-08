terraform {
  required_version = ">= 1.1.7"

  #   backend "s3" {
  #     bucket = "punch-apollo-hr"
  #     key    = "terraform.tfstate"
  #     region = "ap-northeast-1"
  #   }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.13"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

provider "archive" {}
