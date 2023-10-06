import firebase_admin
from firebase_admin import credentials, storage

def get_all_emails():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()

    # Extract the name of each blob (which is the email in your case)
    emails = [blob.name for blob in blobs]
    return emails

<<<<<<< HEAD
def delete_email_from_storage(email):
    """
    Delete a specific email-credential pair from Firebase Cloud Storage.
    """
    bucket = storage.bucket()
    blob = bucket.blob(email)  # Get a reference to the blob
    blob.delete()              # Delete the blob

    print(f"Deleted {email} from storage.")

=======
>>>>>>> 6588927f01f30ab668f02df8480384efcd6551ec
if __name__ == "__main__":
    cred = credentials.Certificate('firebase_secrets.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'userbot-285810.appspot.com'
    })
<<<<<<< HEAD
    delete_email_from_storage("shivammittal2124@gmail.com")
    delete_email_from_storage("shivammittal2124work@gmail.com")
=======
>>>>>>> 6588927f01f30ab668f02df8480384efcd6551ec
    print(get_all_emails())