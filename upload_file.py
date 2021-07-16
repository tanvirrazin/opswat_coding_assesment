import sys
import requests, hashlib, json, time


# Place own APIKEY here
APIKEY = ''


def display_scan_result(scan_report_body):
	"""
	This function displays the information from the response body
	"""
	print("\n\nResult:\n-------")
	print("filename: {}".format(scan_report_body['file_info']['display_name']))
						
	# Detecting if the scan got any threat from all the scanning engines
	if scan_report_body['scan_results']['scan_all_result_a'] == 'No Threat Detected':
		print("overall_status: Clean")
	else:
		print("overall_status: {}".format(scan_report_body['scan_results']['scan_all_result_a']))
	
	# Displaying individual scan result from each engine
	for k in scan_report_body['scan_results']['scan_details']:
		print("engine: {}".format(k))
		print("threat_found: {}".format(scan_report_body['scan_results']['scan_details'][k]['threat_found'] or 'Clean'))
		print("scan_result: {}".format(scan_report_body['scan_results']['scan_details'][k]['scan_result_i']))
		print("def_time: {}".format(scan_report_body['scan_results']['scan_details'][k]['def_time']))

	print("END")


def check_hash_lookup(readable_hash):
	"""
	This function will check with hash lookup API 
	if the file has already been scanned earlier
	If already scanned it will get the results and display
	Otherwise it will return False, which indicates that no scan result was found against the given hash.
	"""
	hash_check_req = requests.get(
		url='https://api.metadefender.com/v4/hash/{}'.format(readable_hash),
		headers={
			'apikey': APIKEY
		}
	)

	scan_report_body = json.loads(hash_check_req.text)
	if hash_check_req.status_code == 200:
		# Previously scanned result was found for this file
		# So no need to upload anymore
		print("Previous scan result found ...")
		display_scan_result(scan_report_body)
		return True

	else:
		# This file was not scanned previously
		# So we have to upload the file now
		print(scan_report_body['error']['messages'][0])
		return False


def upload_file_to_scan(file, file_name):
	"""
	This function will upload the given file in byte format
	If successful, it will return the data_id
	"""
	upload_file_req = requests.post(
		url='https://api.metadefender.com/v4/file', 
		files={'upload_file': file},
		headers={
			'apikey': APIKEY,
			'filename': file_name.rsplit('/')[-1],
			'content-type': 'application/octet-stream'
		}
	)

	upload_file_body = json.loads(upload_file_req.text)

	if upload_file_req.status_code != 200:
		# Error happened while uploading file
		print(upload_file_body['error']['messages'][0])
		return None

	else:
		# File upload was successful
		print("File upload completed.")
		data_id = upload_file_body['data_id']
		return data_id


def retrieve_file_scan_result(data_id):
	"""
	This function will try to call the REST API for retrieving the scan result against data_id
	Until the scan is completed, the API will be called every two seconds.
	"""
	print("Collecting scan report ...")

	while True:
		# Trying to get the scan result with 2 seconds interval
		time.sleep(2)

		scan_report_req = requests.get(
			url='https://api.metadefender.com/v4/file/{}'.format(data_id),
			headers={
				'apikey':APIKEY
			}
		)

		scan_report_body = json.loads(scan_report_req.text)

		if scan_report_req.status_code == 200:

			if scan_report_body['scan_results']['scan_all_result_a'] != 'In Progress':
				# Scan completed, result retrieved
				display_scan_result(scan_report_body)
				break

			else:
				# Scan is not completed yet
				# Trying again in 2 seconds
				print("Still in Progress")
				continue

		else:
			# Some error happened
			# Trying again in 2 seconds
			print(scan_report_body['error']['messages'][0])
			continue


if __name__ == "__main__":

	if len(sys.argv) < 2:
		# Input filename should be provided
		print("Usage: python upload_file.py <file_name>")

	else:
		# Filename taken from command-line argument
		file_name = sys.argv[1]

		# File read and sha1 hash is calculated
		file = open(file_name, 'rb')
		bytes = file.read()
		readable_hash = hashlib.sha1(bytes).hexdigest()
		print("File sha1 hash: {}".format(readable_hash))

		print("Checking hash lookup ...")

		# Checking with hash if scan result already available
		if not check_hash_lookup(readable_hash):
			print("Uploading file now ...")

			# Previous result was not found
			# So uploading file now
			data_id = upload_file_to_scan(file, file_name)

			if data_id is not None:
				# File upload was successfule
				# Now retrieving scan result
				retrieve_file_scan_result(data_id)
					

