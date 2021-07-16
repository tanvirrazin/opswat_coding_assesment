import sys
import requests, hashlib, json, time


# put own APIKEY here
APIKEY = '00a56de6dfe708484fa7d61bbbb891f4'


# This function displays the information from the response body
def display_scan_result(scan_report_body):

	print()
	print("filename: {}".format(scan_report_body['file_info']['display_name']))
						
	# Detec
	if scan_report_body['scan_results']['scan_all_result_a'] == 'No Threat Detected':
		print("overall_status: Clean")
	else:
		print("overall_status: {}".format(scan_report_body['scan_results']['scan_all_result_a']))
	

	for k in scan_report_body['scan_results']['scan_details']:
		print("engine: {}".format(k))
		print("threat_found: {}".format(scan_report_body['scan_results']['scan_details'][k]['threat_found'] or 'Clean'))
		print("scan_result: {}".format(scan_report_body['scan_results']['scan_details'][k]['scan_result_i']))
		print("def_time: {}".format(scan_report_body['scan_results']['scan_details'][k]['def_time']))

	print("END")



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

	# Checking with hash lookup API if the file has already been scanned earlier
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
		display_scan_result(scan_report_body)

	else:
		# This file was not scanned previously
		# So we have to upload the file now
		print(scan_report_body['error']['messages'][0])
		print("Uploading file now ...")

		# Uploading the file in byte format
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

		else:
			# File upload was successful
			print("File upload completed.")
			print("Collecting scan report ...")

			data_id = upload_file_body['data_id']

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
				

