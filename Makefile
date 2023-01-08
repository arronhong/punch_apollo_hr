SRC_DIR=src

punch_in:
	@env `cat .env | xargs` python3 $(SRC_DIR)/punch_apollo_hr.py punch_in $(location)

punch_out:
	@env `cat .env | xargs` python3 $(SRC_DIR)/punch_apollo_hr.py punch_out $(location)

punch_lambda:
	@env `cat .env | xargs` python3 $(SRC_DIR)/lambda_handler.py

test_lambda:
	@env `cat .env | xargs` python3 lambda_handler.py
