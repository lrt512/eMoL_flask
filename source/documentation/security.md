#  Security

As eMoL holds personal information about combatants, it is a requirement by Canadian (and other jurisdictions) law to protect that data 
appropriately..

The data held by eMoL that will be protected includes:
- Legal Name
- Address
- Phone Number
- Date of Birth (for minors)
- SCA member number
- SCA member expiry

Note that email is *not* included in the protected data as it is used as the unique key for each combatant.
 
A combatant record is stored in the database like this:

        {
            email: <email address>
            sca_name: <sca_name>
            encrypted: <all the above data>
            <auth data, etc.>
        }
        
## Access
For users of the system (Ministers of the List, Kingdom Marshals, etc.) there are two roles for dealing with combatant personal information 
that can be assigned to users: read and write. Obviously, write implicitly grants read permission. Users that are not assigned one of these 
permissions will never be able to see combatant personal information.

Combatants may also request self-serve to modify their personal information. In this case, the combatant will click the "I need to 
update my information" button on the welcome page. They will be prompted to enter their email address. Assuming the email address 
given matches the combatant's email address of record, they will be emailed a time-limited and one-time use link to click that will 
allow them to change any personal information element, except for email address (this must be done through the appropriate system user, 
e.g. Minister of the Lists).

## Data at Rest
All encrypted data is encrypted via AES-256, with the encryption key set at initial system setup. (Eventually there will be a mechanism to
 change the key and decrypt/re-encrypt all combatant records.)
 
Whenever a combatant is fetched for viewing or modification, the personal information is decrypted and transmitted to the user performing
the action (see Data in Transit). When combatant information is saved, their personal information is re-encrypted and stored in their
database record as above.
 
## Data in Transit
It is recommended that eMoL be configured to use SSL connections at all times to protect combatant personal information in transit.
 
# Combatant Opt-Out
In keeping with privacy laws ([in Canada, PIPEDA](https://www.priv.gc.ca/leg_c/leg_c_p_e.asp)), whenever a combatant is added to the system 
an email is sent to the combatant that will give the system privacy policy, which will outline these policies and other privacy elements as 
required. This includes an agree/do not agree choice. Any combatant that declines the privacy policy will be deleted from the system, and 
the relevant user(s) notified that the combatant requires manual recordkeeping. 