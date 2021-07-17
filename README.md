

# opswat_coding_assesment


## Instructions to run the code
1. Create a conda environment with python3 with "conda create --name <env_name> python=3.6 requests"
2. Activate conda environment with "conda activate <env_name>"
3. Clone this repository from github.
4. Run the script "upload_file.py" with a files relative address with command "python upload_file.py /path/to/file"

## Work procedure
 At the begining of the program I wrote 4 methods -
	 - display_scan_result
	 - check_hash_lookup
	 - upload_file_to_scan
	 - retrieve_file_scan_result
	
**display_scan_result**: This method takes care of how a scan result for a file should be formatted and displayed. It takes a scan-result in a python dictionary format as input. From outside the method, we are parsing the scan result part from a REST API response, converting it to a python dictionary  and passing it to this method. And the method displays it on the console itself.

**check_hash_lookup**: This method is responsible for calling the REST API with a hash-value to check if the system already has a scan result saved against this hash-value. So it takes a hash-value in string format as input, calls "https://api.metadefender.com/v4/hash/:hash" API endpoint. If the request status-code is not 200, it means no scan result was found. It displays the error-message on the terminal and returns False. But if the status-code is 200, it means a scan-result was found for this hash-value. Then it calls "display_scan_result" method with the response body in a dictionary format and returns True.

**upload_file_to_scan**: This method takes care of uploading a file to the system using the REST API endpoint "https://api.metadefender.com/v4/file" using the APIKEY, filename and content-type in headers. As "content-type" we used "application/octet-stream" because I uploaded the file in byte format and that was preferred (compared to multpart/form-data). We used POST method to call this REST API and as payload we sent the given file in byte format. The method takes a file (in byte format) and a file_name (in string format). The method calls the API endpoint with POST method. If successful, the API gives us back a "data_id" which is a specific ID for this upload, and later we can use this "data_id" to retrieve the scan result for this file.

**retrieve_file_scan_result**: This method is responsible to collect the scan result. It takes a "data_id" and calls the REST API endpoint "https://api.metadefender.com/v4/file/:dataId" with GET method. Now there is an interesting point. After uploading a file it takes some time to complete the scan. The time varries depending on the file size and the number of scanning engines. So if we call the scan-result retrieving API right after uploading the file, we may not get any result. But if we call after sometime, the scanning mechanism may complete by that time and we may get the result. So in our program, it is calling the retrieving API 2 seconds after the file-upload API call is successful. If the "['scan_results']['scan_all_result_a']" field is "In Progress", we can understand that the scan is not completed yet. Then the method again waits 2 seconds and then calls the API again. And this continues until the scan-result is available.

**Main method**: In the main method, we took the file-name from command line argument. We expect it to be a relative address for the file. Then we read the file in byte format. Next we calculate the sha1 hash-value using the hashlib library in python. Using this hash-value, we are calling "check_hash_lookup" method to check if there is already a scan-result for this hash-value. If there is any, the method itself is displaying the result to the output. If not, we are calling "upload_file_to_scan" method to upload the file. It gives us back the "data_id". Using this, we call the method "retrieve_file_scan_result" method to get and display the scan-result.

**Problem faced**: We faced a problem with the hash-value. Let's say we have upload a file and got the scan-result of it. When we are working with the same file again, we assume the hash-value we generate this time, is as same as the previous time. Because our assumption is, everytime we generate hash-value for the same file using the same algorithm, the hash-value should be same all the time. But when we are generating sha1 hash-value of a file, and after uploading the file API is giving a sha1 hash-value, these two values are not same. In fact most interesting part is, each time we generate sha1 hash-value using hashlib in python, we get the same value. But each time we upload the same file to metadefender API, it gives back a sha1 hash-value, and each time it is different. Also when we see the hash value in the submission history, each time we see the hash-value (we assume it is sha1 value) different. But we assume, everytime we generate a hash-value, should be same each time. Now we are a bit confused how that hash-value is generated or how should we generate the hash value. So we could not make the hash-value checking part work properly, but when we called hash-check API with hardcoded hash-value (sha1 value from the response body of file upload API), we that saw it is working good.