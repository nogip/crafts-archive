# Innopolis <3
╔══╗╔╗─╔╗╔╗─╔╗╔══╗╔═══╗╔══╗╔╗──╔══╗╔══╗
╚╗╔╝║╚═╝║║╚═╝║║╔╗║║╔═╗║║╔╗║║║──╚╗╔╝║╔═╝
─║║─║╔╗─║║╔╗─║║║║║║╚═╝║║║║║║║───║║─║╚═╗
─║║─║║╚╗║║║╚╗║║║║║║╔══╝║║║║║║───║║─╚═╗║
╔╝╚╗║║─║║║║─║║║╚╝║║║───║╚╝║║╚═╗╔╝╚╗╔═╝║
╚══╝╚╝─╚╝╚╝─╚╝╚══╝╚╝───╚══╝╚══╝╚══╝╚══╝

Here all "homeworks" for last 6 month.

I'd like you check folders whose names start with "#" 
because projects in them are more massive than in other folders.

---
**#MorrisBot_project:**
- EventHandler.py
- BotAccount.py
- modules
-- commands
-- database
-- ege_parser
-- group_manager
-- march8
- ...and other files...

// This bot for communities in vk.com
// It can broadcast messages from administrators to members and answer to commands from members.
// So, you can test it..
// For testing you need to: 1) create community, 2) generate an API token, 3) launch the bot with the parameter "-T your_token".
// Then write the message to the community with "/all" on the beginning to broadcast it to the members, or "/mdr" to broadcast to the administrators.
// Some modules are need an additional parameter - BotAccount.  
// It is the "fake" member without any priveleges. This hack provides the ability to analyze the wall, discussion boards, etc.
// To add this account add the parameters "-l login -p password".
// Since these functions will not be described here, I advise you not to test them.

---
**#hacktool:**
- ReverseShellServer.py
- VictimShell.py
- ip_packet_parser.py
- trojan
-- create_script.py
-- mse.py
-- shell.py

---
**#vk_utils**
- friend_likes_post.py
- restore_removed_chat.py
- steal_vk_messages.py
