

process_data:
	pipenv run python3 preprocess_data.py --raw_data_path ../data --dest_path ./output

train:
	pipenv run python3 train.py --data_path ./output

hpo:
	pipenv run python3 hpo.py --data_path ./output

register_model:
	pipenv run python3 register_model.py --data_path ./output
