import time
import logging
import configparser
import os
from subprocess import Popen, PIPE

from datetime import datetime, timedelta

from azure.storage.blob import BlobServiceClient, generate_account_sas, ResourceTypes 
from azure.storage.blob import AccountSasPermissions, BlobClient, ContainerClient

# LINK 1: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python
# LINK 2: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/storage/azure-storage-blob

def _load_sas_token(storage_account, account_key):
	# SAS TOKEN: https://docs.microsoft.com/en-us/rest/api/storageservices/create-account-sas#account-sas-permissions-by-operation
	sas_token = generate_account_sas(
		account_name=storage_account,
		account_key=account_key,
		resource_types=ResourceTypes(service=True, container=True, object=True),
		permission=AccountSasPermissions(read=True, create=True),
		expiry=datetime.utcnow() + timedelta(hours=12)
	)
	return sas_token

def _load_connection_string(resource_group, storage_account):
	cmd_list = "az storage account show-connection-string -g {} -n {}".format(
		resource_group, storage_account).split(' ')
	print(cmd_list)

	p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	output, err = p.communicate(b"input data that is passed to subprocess' stdin")
	rc = p.returncode

	print(">> CONNECTION STRING:", output, type(output))
	print("ERROR:", err)
	return output

def init_azure_storage(resource_group, storage_account, account_key, method):
	print("\t [ ENTER init_azure_storage() ]")


	if method is 'str':
		print("\t [A] CONNECTING TO AZURE STORAGE with Connection String METHOD")
		connect_str = _load_connection_string(resource_group, storage_account)

		# Create the BlobServiceClient object which will be used to create a container client
		az_storage_client = BlobServiceClient.from_connection_string(connect_str)
	elif method is 'sas':
		print("\t [A] CONNECTING TO AZURE STORAGE with SAS METHOD")
		sas_token = _load_sas_token(storage_account, account_key)
		az_storage_client = BlobServiceClient(account_url="https://storageaccountreclab87d.blob.core.windows.net", credential=sas_token)

	return az_storage_client

def upload_wav2blob(az_storage_client, container_name, blob_name, node_wav):
	## Functionaliity of Block Blob(): https://github.com/Azure-Samples/storage-blob-python-getting-started/blob/master/blob_basic_samples.py#L77

	# Create a blob client using the local file name as the name for the blob
	blob_client = az_storage_client.get_blob_client(container=container_name, blob=blob_name)

	# Upload the created file
	# with open(node_wav, "rb") as data:
	blob_client.upload_blob(node_wav)

	print("\nUploaded to Azure Storage as blob:\n\t{}".format(blob_name))

	return blob_client

def download_blob(az_storage_client, container, blob_name):
	## Getting BlobClient of txt File
	blob = az_storage_client.get_blob_client(container=container, blob=blob_name)

	## Download and Read Blob Data
	tic = time.time()
	print('\t [A] Downloading Blob')
	download_stream = blob.download_blob()

	print('\t [B] Reading Blob')
	wav = download_stream.readall()
	with open('temp.wav', "wb") as my_blob:
		my_blob.write(wav)
	print("\t[Time Taken] Download & Read Blob: {:.4f} sec".format(time.time() - tic))
	return wav


def list_blobs(container_client):
	print("\nListing blobs...")
	blob_list = container_client.list_blobs()
	for blob in blob_list:
	    print("\t" + blob.name)

