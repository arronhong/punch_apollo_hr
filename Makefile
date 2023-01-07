punch_in:
	@env `cat .env | xargs` python3 main.py punch_in $(location)

punch_out:
	@env `cat .env | xargs` python3 main.py punch_out $(location)
