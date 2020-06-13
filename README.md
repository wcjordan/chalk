# chalk
Todo app

Setup
-----
Copy .env_default to .env
Generate secret key running:
python -c "from django.utils.crypto import get_random_string; chars = 'abcdefghijklmnopqrstuvwxyz0123456789\!@#$%^&\*(-\_=+)'; print(get_random_string(50,chars))"
set SECRET_KEY in .env

To prevent docker conflicting with the corporate subnet
As root, create /etc/docker/daemon.json with the content
{
  "bip": "10.1.10.1/24"
}