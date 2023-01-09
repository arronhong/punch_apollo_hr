SRC_DIR=src
TF_DIR=terraform

punch_in:
	@env `cat .env | xargs` python3 $(SRC_DIR)/punch_apollo_hr.py punch_in $(location)

punch_out:
	@env `cat .env | xargs` python3 $(SRC_DIR)/punch_apollo_hr.py punch_out $(location)

punch_lambda:
	@env `cat .env | xargs` python3 $(SRC_DIR)/lambda_handler.py

plan:
	@env `awk '{print "TF_VAR_" $$0}' .env | xargs` terraform -chdir=$(TF_DIR) plan

apply:
	@env `awk '{print "TF_VAR_" $$0}' .env | xargs` terraform -chdir=$(TF_DIR) apply

destroy:
	@env `awk '{print "TF_VAR_" $$0}' .env | xargs` terraform -chdir=$(TF_DIR) destroy
