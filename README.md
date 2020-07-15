# chalk
Todo app

Setup
-----
Copy .env_default to .env
Set SECRET_KEY & DB_PASS in .env
  These should be random secure strings
  e.g. head -c 32 /dev/urandom | base64

To prevent docker conflicting with the corporate subnet
As root, create /etc/docker/daemon.json with the content
{
  "bip": "10.1.10.1/24"
}