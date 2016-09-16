**Slack Single Channel**

Displays a single channel, chosen from the drop down at the top. Post messages to the same channel.

We changed to slack at work and while 90% of the things were better than Skype, I missed being able
to have a group in a separate windows so I could alt-tab and check it, hover over it and see if any
new messages had been posted to that particular channel.

There were many slack client libraries available but no actual front ends.
 
Requires your API token from the slack website, entered in the ini file passed as the first argument:

`python slacksinglechannel.py config.ini`


options in config.ini:

`[default]`

`token = yourtokenhere`

`channel = defaultchannelname`

`logging = n`

Logging set to y just logs a stream of the events from slack to 'eventlog.log' in the working directory.
If you are going to run more that one, the log file will flip out so do them in different directories or set logging to n.


TODO: message groups as well as channels, save and restore of messages, improve or remove logging.


Thanks to https://github.com/slackhq/python-slackclient for the actual difficult bit :)