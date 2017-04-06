### Usage
```bash
usage: aws_ssh_tags.py [-h] --region REGION --user USER --tags TAGS
                       --privatekey PRIVATEKEY [--cmd-list CMD_LIST]
                       [--file-origin FILE_ORIGIN] [--file-dest FILE_DEST]

optional arguments:
  -h, --help                  show this help message and exit
  --region REGION             AWS Region
  --user USER                 SSH Username
  --tags TAGS                 AWS Tags to filter, in json format.
  --privatekey PRIVATEKEY     relative path of privatekey
  --cmd-list CMD_LIST         list of commands comma separated
  --file-origin FILE_ORIGIN   relative path of the file you will send
  --file-dest FILE_DEST       absolute path of the destination
```