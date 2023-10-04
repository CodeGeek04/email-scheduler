import firebase_admin
from firebase_admin import credentials, storage

def get_all_emails():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()

    # Extract the name of each blob (which is the email in your case)
    emails = [blob.name for blob in blobs]
    return emails

if __name__ == "__main__":
    cred = credentials.Certificate('firebase_secrets.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'userbot-285810.appspot.com'
    })
    print(get_all_emails())