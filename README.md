# HLL_CRCON_Forbid_role

A plugin for Hell Let Loose (HLL) CRCON (https://github.com/MarechJ/hll_rcon_tool)
that blocks role(s) access to defined players.

![375492543-27dd6f25-13ed-45b5-9f7e-ed5ceee5d28f](https://github.com/user-attachments/assets/2cdea1c1-0fcd-403b-8011-0a9bd217e3ad)

> [!NOTE]
> The shell commands given below assume your CRCON is installed in `/root/hll_rcon_tool`.  
> You may have installed your CRCON in a different folder.  
>   
> Some Ubuntu Linux distributions disable the `root` user and `/root` folder by default.  
> In these, your default user is `ubuntu`, using the `/home/ubuntu` folder.  
> You should then find your CRCON in `/home/ubuntu/hll_rcon_tool`.  
>   
> If so, you'll have to adapt the commands below accordingly.

## Install
- Copy `restart.sh` in CRCON's root (`/root/hll_rcon_tool/`) ;
- Create a `custom_tools` folder in CRCON's root (`/root/hll_rcon_tool/`) ;
- Copy these files into the newly created `/root/hll_rcon_tool/custom_tools/` folder :
  - `common_functions.py`
  - `common_translations.py`
  - `automod_forbid_role.py`
  - `automod_forbid_role_config.py`
- Edit `/root/hll_rcon_tool/config/supervisord.conf` to add this bot section : 
  ```conf
  [program:automod_forbid_role]
  command=python -m custom_tools.automod_forbid_role
  environment=LOGGING_FILENAME=automod_forbid_role_%(ENV_SERVER_NUMBER)s.log
  startretries=100
  startsecs=10
  autostart=false
  autorestart=true
  ```

## Config
- Edit `/root/hll_rcon_tool/custom_tools/automod_forbid_role_config.py` and set the parameters to fit your needs ;
- Restart CRCON :
  ```shell
  cd /root/hll_rcon_tool
  sh ./restart.sh
  ```

## Limitations
⚠️ Any change to these files requires a CRCON rebuild and restart (using the `restart.sh` script) to be taken in account :
- `/root/hll_rcon_tool/custom_tools/common_functions.py`
- `/root/hll_rcon_tool/custom_tools/common_translations.py`
- `/root/hll_rcon_tool/custom_tools/automod_forbid_role.py`
- `/root/hll_rcon_tool/custom_tools/automod_forbid_role_config.py`

⚠️ This plugin requires a modification of the `/root/hll_rcon_tool/config/supervisord.conf` file, which originates from the official CRCON depot.  
If any CRCON upgrade implies updating this file, the usual upgrade procedure, as given in official CRCON instructions, will **FAIL**.  
To successfully upgrade your CRCON, you'll have to revert the changes back, then reinstall this plugin.  
To revert to the original file :  
```shell
cd /root/hll_rcon_tool
git restore config/supervisord.conf
```
