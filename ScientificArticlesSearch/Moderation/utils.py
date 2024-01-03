from django.core.mail import send_mail
from django.conf import settings

def send_moderator_account_create_email(username, email, nom, prenom):
    subject = 'Notification de création de compte moderateur'
    
    message = f'''
    Bonjour Modérateur,

    Un compte a été créé avec les détails suivants :
    
    Nom d'utilisateur : {username}
    Email : {email}
    Nom : {nom}
    Prenom : {prenom}
    
    Un mot de passe temporaire a été généré pour cet utilisateur.

    Vous devez changer ce mot de passe dès sa première connexion pour des raisons de sécurité.

    Merci,
    Votre équipe d'application
    '''
    html_message = f'''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notification de création de compte</title>
    </head>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; border-radius: 10px;">
            <h2 style="color: #333;">Notification de création de compte</h2>
            <p style="color: #555;">
                Bonjour {nom.upper() + " " + prenom},
            </p>
            <p style="color: #555;">
                Un compte a été créé avec les détails suivants :
            </p>
            <ul>
                <li><strong>Nom d'utilisateur :</strong> {username}</li>
                <li><strong>Email :</strong> {email}</li>
                <li><strong>Nom :</strong> {nom}</li>
                <li><strong>Prenom :</strong> {prenom}</li>
            </ul>
            <p style="color: #555;">
                Un mot de passe temporaire a été généré pour cet utilisateur. Veuillez informer l'utilisateur de son existence.
            </p>
            <p style="color: #555;">
                L'utilisateur devra changer ce mot de passe dès sa première connexion pour des raisons de sécurité.
            </p>
            <p style="color: #555;">
                Merci,
                <br>
                Votre équipe d'application
            </p>
        </div>
    </body>
    </html>
    '''
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
        html_message=html_message
    )
