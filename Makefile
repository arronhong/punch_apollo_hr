punch_in:
	@env `cat .env | xargs` python3 punch_apollo_hr.py punch_in $(location)

punch_out:
	@env `cat .env | xargs` python3 punch_apollo_hr.py punch_out $(location)

test_lambda:
	@env `cat .env | xargs` python3 lambda_handler.py
