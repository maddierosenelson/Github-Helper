The github-helpers API allows you to scan through all your team's
repositories and list which repositories have open pull requests. Additionally,
the program can list who created the PR, who has contributed to the PR, and when
it was last updated. You can also look for open PRs using a search term.

To use github-helpers complete the following steps:

#Install pip using:
`sudo easy_install pip`

Then install requests and terminaltables using: 
`pip install requests`
`pip install terminaltables`

#Install virtual enburrito using the information at the following link:
https://fanatics.atlassian.net/wiki/spaces/LABS/pages/43319640/Environment+Setup

the command is: `curl -sL https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh`


Add the following text to your .zprofile or .bashrc
# startup virtualenv-burrito
`if [ -f $HOME/.venvburrito/startup.sh ]; then
    . $HOME/.venvburrito/startup.sh
fi`


Run `mkvirtualenv github-helpers`

To run use `python get_prs.py -{X} "{XXXXX}"`
 
with the desired input of username (-u), repository name (-r), contributor (-c), X days old (-x), or search term (-s).

A summary of all the open PRs will always be returned before the tables are returned. To disable this, comment out the line `print '({}) PRs found for {}'.format(len(prs), repo['name'])`. This summary will be returned regardless of whether a username was inputted correctly or the days input was an invalid input.

Username input and contributor input both use login information (the string before @fanatics.com in ever email). The number inputted for X days old must be greater than 0.

If `python get_prs.py -r "all"` is run, all of the open PRs in all the repos will be printed.
If `python get_prs.py -c "all"` is run, all of the open PRs in all the repos will be printed with all contributors for each open PR also printed.

All the open PRs printed in the table are always printed from oldest to newest with regard to when they were last updated.
