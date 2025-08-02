from flask_mail import Message
from flask import current_app
from app import mail
import threading

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body=None):
    """Send email with the given parameters."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    # Send email asynchronously
    thread = threading.Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_todo_creation_email(user_email, todo_title):
    """Send email notification when a new todo is created."""
    subject = "New Todo Created - TodoApp"
    sender = current_app.config['MAIL_USERNAME']
    recipients = [user_email]
    
    text_body = f"""
    Hello!
    
    A new todo has been created in your TodoApp account:
    
    Title: {todo_title}
    
    You can manage your todos by logging into your account.
    
    Best regards,
    TodoApp Team
    """
    
    html_body = f"""
    <html>
      <body>
        <h2>New Todo Created</h2>
        <p>Hello!</p>
        <p>A new todo has been created in your TodoApp account:</p>
        <p><strong>Title:</strong> {todo_title}</p>
        <p>You can manage your todos by logging into your account.</p>
        <p>Best regards,<br>TodoApp Team</p>
      </body>
    </html>
    """
    
    send_email(subject, sender, recipients, text_body, html_body)
