from haikunator import Haikunator
import datetime

haikunator = Haikunator()
epoch = datetime.datetime.utcfromtimestamp(0)

def generate_random_model_name():
	return haikunator.haikunate(token_length=0)


def convert_dt_to_epoch(dt):
    return (dt - epoch).total_seconds() * 1000.0