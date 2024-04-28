## Labelstudio
The helper script has a function to create a user. However this does not set a password and return it. To set a password you need to exec into the labelstudio pod and
run 
```bash
label-studio reset_password --username <email>
```
The passwords can all be put in the accout section of our wiki. There not really secret.

Deleting a user is only possible via API. We still need to implement a function for this.