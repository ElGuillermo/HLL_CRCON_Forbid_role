# HLL_CRCON_Forbid_roles

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that blocks role(s) access to defined players.

![375492543-27dd6f25-13ed-45b5-9f7e-ed5ceee5d28f](https://github.com/user-attachments/assets/2cdea1c1-0fcd-403b-8011-0a9bd217e3ad)

Install (open this file for complete procedure) :
- Create a `custom_tools` folder in CRCON's root (`/root/hll_rcon_tool/`) ;
- Copy `automod_forbid_role.py` in `/root/hll_rcon_tool/custom_tools/` ;
- Copy `custom_common.py` in `/root/hll_rcon_tool/custom_tools/` ;
- Copy `custom_translations.py` in `/root/hll_rcon_tool/custom_tools/` ;
- Copy `restart.sh` in CRCON's root (`/root/hll_rcon_tool/`) ;
- Edit `/root/hll_rcon_tool/config/supervisord.conf` to add this bot section : 
  ```conf
  [program:automod_forbid_role]
  command=python -m custom_tools.automod_forbid_role
  environment=LOGGING_FILENAME=automod_forbid_role_%(ENV_SERVER_NUMBER)s.log
  startretries=100
  startsecs=60
  autostart=false
  autorestart=true
  ```

Config :
- Edit `/root/hll_rcon_tool/custom_tools/automod_forbid_role.py` and set the parameters to your needs ;
- Restart CRCON :
  ```shell
  cd /root/hll_rcon_tool
  sh ./restart.sh
  ```
Any change to these files :
- `/root/hll_rcon_tool/custom_tools/automod_forbid_role.py` ;
- `/root/hll_rcon_tool/custom_tools/custom_common.py` ;
- `/root/hll_rcon_tool/custom_tools/custom_translations.py` ;  
...will need a CRCON restart (using `restart.sh` script) to be taken in account.
