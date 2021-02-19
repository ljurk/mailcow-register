an extenstion to mailcow that lets you create invitations to register in your mailcow instance

Admin-Tasks:
- create invitation under `/admin`
- set all parameters for the mail account
    - username
    - quota
    - tls in
    - tls out
    - domain
    - active
- it will be saved with a unique token
- a url is created which contains username and token
- send url to user

User-Tasks:
- go to url
- set parameters for the mail account
    - Full Name
    - password
- Submit: Mail-Account will be created
