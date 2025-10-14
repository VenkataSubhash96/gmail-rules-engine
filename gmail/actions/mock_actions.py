def mark_as_read(email_id, *args, **kwargs):
    print(f"[MOCK] mark_as_read called for email_id={email_id}")

def mark_as_unread(email_id, *args, **kwargs):
    print(f"[MOCK] mark_as_unread called for email_id={email_id}")

def move_message(email_id, folder, *args, **kwargs):
    print(f"[MOCK] move_message called for email_id={email_id}, folder={folder}")
