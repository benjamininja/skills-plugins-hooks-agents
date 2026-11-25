Tier: <haiku | low | medium | high>
Ticket: #<n>
Base: origin/main <or origin/<branch> of an open PR in this repository, for a stacked brief; the manager passes it to dispatch.ps1 as -Base>
venv: <yes | no>
Profile: <optional: a profile from the owner's profiles file, for example research or probe; leave the line out for none>
Hosts: <with Profile: probe only, the hosts the probe may reach; the script's ALLOWED_HOSTS is checked against them at closeout>

<What to do, in plain words. No double quote anywhere in this file.>

Files: <for a low brief, the files to touch>
Question: <for a medium brief, what to find out, where to start, and the shape of the answer>

Done when: <the condition, checkable>
Proof: <the exact command or commands, each one a builder may run; or: manager runs it>

Park, do not decide: <what in this work is the owner's>
