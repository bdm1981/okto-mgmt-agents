# Team roles

`roleId` from `list_users` does **not** distinguish OktoRocket's internal teams — nearly every
staff member carries `Advisor` (roleId 1), which is the shop-facing role name inherited from the
product's own permission model, not a description of what the person does here.

So the technician / customer-success split lives in this file. Keep it current; the skill reads it
verbatim and treats anyone missing as `unclassified`.

Team values in use: `Support`, `Success`, `Sales`, `Billing`, `Installer`, `Marketing`, `Development`, `management`, `exclude`. Spelling matters -- the scripts group on the literal string.
Use `exclude` for test lines, lab phones, and shared/system extensions.

| Ext  | Name              | Team          |
|------|-------------------|---------------|
| 8033 | Jordan Carter     | Support       |
| 8030 | Justin Curcio     | Support       |
| 8039 | Tucker Hensley    | Support       |
| 8042 | Tristan Phifer    | Support       |
| 8036 | Cristina Pascoal  | Success       |
| 8053 | Tonya Buffington  | Billing       |
| 8044 | Scott Maloney     | Installer     |
| 8032 | Albert Lee        | Sales         |
| 8021 | Manuel Chachere   | Support       |
| 8031 | Allie Gratton     | Success       |
| 8052 | Matt Munoz        | Sales         |
| 8035 | Shawn Richards    | Support       |
| 8038 | Jada Baker        | Success       |
| 8045 | MiMi Williams     | Marketing     |
| 8013 | Nathan Arnold     | Development   |
| 8005 | TeDarrell Cantrell| Success       |
| 8022 | Cole Nussear      | Development   |
| 8009 | Katie Wolf        | Success       |
| 8010 | Stephen Little    | Development   |
| 8011 | Aaron Viratos     | Success       |
| 8025 | Keith Twitchel    | Sales         |
| 8043 | Jake Vinson       | management    |
| 8037 | Jay Power         | management    |
| 8034 | Shawn Strong      | management    |
| 8051 | Tyrone Hill       | management    |
| 8007 | Brad McAllister   | management    |
| 8024 | Rick Buffington   | management    |
| 8054 | AfterHours Line   | exclude       |
| 8008 | click-to-call     | exclude       |
| 8002 | DC Support        | exclude       |
| 8097 | Jake 8097 Test    | exclude       |
| 8098 | Lab Test Phone    | exclude       |
| 8083 | Jake 8083         | exclude       |
| 9001 | Test SA Jake      | exclude       |
| 8000 | (unknown/system)  | exclude       |
| 8765 | (unknown/system)  | exclude       |

## Ambiguous extensions

These extensions map to more than one user account. The skill picks the active account with the
most recent `lastLogin`; the choice recorded here wins if you set one.

| Ext  | Candidates                                    | Resolved to      |
|------|-----------------------------------------------|------------------|
| 8036 | Daniel Gans, Cristina Pascoal                 | Cristina Pascoal |
| 8043 | Matt Folmar (Admin), Jake Vinson (Site Mgr)   | Jake Vinson      |
| 8031 | Patrick Neprud (Site Mgr), Allie Gratton      | Allie Gratton    |
| 8021 | Manuel Chachere, "Front Counter 1" (Phone Only)| Manuel Chachere |
| 8013 | Jeremy Johnson, Nathan Arnold                 | Nathan Arnold    |
| 8025 | Keith Twitchel, "Android Test"                | Keith Twitchel   |
