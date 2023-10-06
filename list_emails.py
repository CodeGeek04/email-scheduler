import firebase_admin
from firebase_admin import credentials, storage

def get_all_emails():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()

    # Extract the name of each blob (which is the email in your case)
    emails = [blob.name for blob in blobs]
    return emails

def delete_email_from_storage(email):
    """
    Delete a specific email-credential pair from Firebase Cloud Storage.
    """
    bucket = storage.bucket()
    blob = bucket.blob(email)  # Get a reference to the blob
    blob.delete()              # Delete the blob

    print(f"Deleted {email} from storage.")

if __name__ == "__main__":
    cred = credentials.Certificate('firebase_secrets.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'userbot-285810.appspot.com'
    })
    delete_email_from_storage("shivammittal2124@gmail.com")
    delete_email_from_storage("shivammittal2124work@gmail.com")
    print(get_all_emails())