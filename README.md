# Have I been pwnd email PDF notifier

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

This repository holds a project which I used to maintain my Python programming skills a little bit.
The functionality of the Python3 file is to check Troy Hunt's database for breaches. The result of 
this is then afterwards put into a generated PDF (LaTeX document). Finally, the Python3 file
sends out an email address to a specific email address with the PDF document in the attachments.

## Requirements

The following additional modules have to be installed in order to use this script.

```
smtp json requests
```

## Usage

Before executing the script, make sure to alter the variables and list below to your needs.
```python
        username = "username"
        password = "password"
        smtp_server = "server"
        to_email = "email@domain.tld"
        from_email = "email@domain.tld"
        email_addr = ["email@domain.tld"]
```

Note that you can configure multiple email addresses in the list structure to be tested.

## Limitations

The file currently has the following limitations of which I plan to fix in the future:

* PGP support for integrity and confidentiality protection.
* A better layout of the PDF document. Currently, the document can be found to be quite ugly :-).
